"""
CUSTOM ADDITION: Adversys API Client Tool
=========================================
This file is a custom addition to Delta for Adversys Core integration.
It provides a base tool for making authenticated API calls to Adversys Core.

This is NOT part of the upstream Delta codebase.
"""
import os
import time
import requests
from typing import Optional, Dict, Any
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.errors import handle_error
from python.helpers import dotenv


class AdversysAPIClient:
    """Client for communicating with the Adversys API service"""
    
    def __init__(self):
        """Initialize API client with configuration from environment variables"""
        # Get API URL from environment (default to localhost)
        self.base_url = (
            dotenv.get_dotenv_value("ADVERSYS_API_URL") or 
            os.getenv("ADVERSYS_API_URL") or 
            "http://127.0.0.1:8000"
        )
        
        # Remove trailing slash
        self.base_url = self.base_url.rstrip('/')
        
        # Get authentication credentials
        # Service accounts should use API key authentication, not password-based login
        # Priority: 1. Encrypted files (production), 2. Environment variable, 3. Database (if accessible)
        self.api_key = ""
        
        # Try to load from encrypted files first (production - most secure)
        self.api_key = self._get_api_key_from_encrypted_files()
        
        # Fall back to environment variable if encrypted files not available
        if not self.api_key:
            self.api_key = (
                dotenv.get_dotenv_value("ADVERSYS_API_KEY") or 
                os.getenv("ADVERSYS_API_KEY") or 
                ""
            )
        
        # If API key still not set, try to retrieve from database (for local development)
        if not self.api_key:
            self.api_key = self._get_api_key_from_database()
        
        # Service accounts use API key authentication only (no password-based login)
        # Username is kept for reference but not used for authentication
        self.api_username = (
            dotenv.get_dotenv_value("ADVERSYS_API_USERNAME") or 
            os.getenv("ADVERSYS_API_USERNAME") or 
            "adversys-service"
        )
        
        # Default timeout for requests (in seconds)
        self.timeout = 30
        
        # SSL verification - use CA bundle if provided (for self-signed certs)
        self.verify_ssl = True
        ca_bundle = (
            dotenv.get_dotenv_value("REQUESTS_CA_BUNDLE") or 
            os.getenv("REQUESTS_CA_BUNDLE") or
            dotenv.get_dotenv_value("SSL_CERT_FILE") or
            os.getenv("SSL_CERT_FILE")
        )
        if ca_bundle:
            if os.path.exists(ca_bundle):
                self.verify_ssl = ca_bundle
                # CA bundle includes system CAs + self-signed Adversys cert
            else:
                PrintStyle().warning(f"CA bundle file specified but not found: {ca_bundle}. SSL verification may fail for self-signed certificates.")
        elif os.getenv("REQUESTS_CA_BUNDLE") == "" or os.getenv("SSL_CERT_FILE") == "":
            # Explicitly disabled
            self.verify_ssl = False
        
        # Session is no longer used (API key authentication only)
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        self.csrf_token: Optional[str] = None
        self.auth_backoff_until = 0.0
    
    def _get_api_key_from_database(self) -> str:
        """
        Try to retrieve API key from the database (for local development convenience).
        This is a fallback when ADVERSYS_API_KEY is not set in environment variables.
        
        Returns:
            API key string, or empty string if not found
        """
        # Try to access the database file (shared with API container in docker-compose)
        db_paths = [
            "/var/lib/adversys/core/adversys.db",  # Production/standard path
            os.path.join(os.path.dirname(__file__), "../../../services/data/adversys.db"),  # Local dev fallback
        ]
        
        for db_path in db_paths:
            if os.path.exists(db_path):
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT api_key FROM users WHERE username = 'adversys-service' AND api_key IS NOT NULL AND api_key != ''"
                    )
                    result = cursor.fetchone()
                    conn.close()
                    if result and result[0]:
                        PrintStyle().info(f"Retrieved API key from database: {db_path}")
                        return result[0]
                except Exception as e:
                    # Silently fail - database might not be accessible or might not exist yet
                    PrintStyle().debug(f"Could not retrieve API key from database at {db_path}: {e}")
                    continue
        
        return ""
    
    def _get_api_key_from_encrypted_files(self) -> str:
        """
        Try to retrieve API key from encrypted files (production - most secure).
        This uses the same encryption scheme as the orchestrator.
        
        Returns:
            API key string, or empty string if not found
        """
        # Master key file paths (check both production and dev paths)
        MASTER_KEY_FILES = [
            "/etc/adversys/core/master-key",  # Production path
            "/var/lib/adversys/core/config/master-key",  # Dev path (for Docker Compose)
        ]
        
        # Encrypted credentials directory paths (check both production and dev paths)
        ENCRYPTED_CREDENTIALS_DIRS = [
            "/etc/adversys/core/encrypted",  # Production path
            "/var/lib/adversys/core/config/encrypted",  # Dev path (for Docker Compose)
        ]
        
        # Try each combination of master key and encrypted directory
        MASTER_KEY_FILE = None
        ENCRYPTED_API_KEY_FILE = None
        
        for master_key_file in MASTER_KEY_FILES:
            for encrypted_dir in ENCRYPTED_CREDENTIALS_DIRS:
                encrypted_api_key_file = f"{encrypted_dir}/adversys-api-key.enc"
                
                # Check if both files exist
                if os.path.exists(master_key_file) and os.path.exists(encrypted_api_key_file):
                    # Use these paths for decryption
                    MASTER_KEY_FILE = master_key_file
                    ENCRYPTED_API_KEY_FILE = encrypted_api_key_file
                    break
            if MASTER_KEY_FILE and ENCRYPTED_API_KEY_FILE:
                break
        
        # If no valid combination found, return empty
        if not MASTER_KEY_FILE or not ENCRYPTED_API_KEY_FILE:
            return ""
        
        # Try to import cryptography
        try:
            from cryptography.fernet import Fernet
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.backends import default_backend
            import base64
        except ImportError:
            PrintStyle().debug("cryptography not available - cannot decrypt credentials from encrypted files")
            return ""
        
        try:
            # Read master key
            with open(MASTER_KEY_FILE, 'rb') as f:
                master_key = f.read().strip()
                if len(master_key) == 0:
                    return ""
            
            # Derive encryption key from master key using PBKDF2
            salt = b'adversys_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            encryption_key = base64.urlsafe_b64encode(kdf.derive(master_key))
            
            # Read encrypted data
            with open(ENCRYPTED_API_KEY_FILE, 'rb') as f:
                encrypted_data = f.read()
                if len(encrypted_data) == 0:
                    return ""
            
            # Decrypt
            fernet = Fernet(encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            api_key = decrypted_data.decode('utf-8')
            
            PrintStyle().info(f"Loaded API key from encrypted files ({ENCRYPTED_API_KEY_FILE})")
            return api_key
            
        except Exception as e:
            PrintStyle().debug(f"Could not decrypt API key from encrypted files ({ENCRYPTED_API_KEY_FILE}): {e}")
            return ""
    
    def _ensure_session(self) -> bool:
        """Ensure we have a valid session cookie by logging in if needed.
        
        Note: Service accounts should use API key authentication only.
        This method is deprecated and will not work for service accounts.
        """
        # Service accounts must use API key authentication
        if self.api_key:
            return True
        
        # No API key - cannot authenticate (service accounts cannot use password login)
        PrintStyle().error("ADVERSYS_API_KEY is required for service account authentication. Password-based login is not supported for service accounts.")
        return False
    
    def request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> requests.Response:
        """
        Make an authenticated API request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., "/api/v1/targets")
            json_data: JSON data for request body
            params: Query parameters
            
        Returns:
            Response object
        """
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Service accounts must use API key authentication
        if not self.api_key:
            PrintStyle().error("ADVERSYS_API_KEY is required. Service accounts cannot use password-based authentication.")
            raise ValueError("ADVERSYS_API_KEY environment variable is required for service account authentication")
        
        headers["X-API-Key"] = self.api_key
        
        try:
            # API key auth - use regular requests (no session needed)
            resp = requests.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            
            if resp.status_code == 401:
                PrintStyle().warning("API key authentication failed. Check that ADVERSYS_API_KEY is set correctly and matches the service account's API key in the database.")
            
            return resp
        except requests.RequestException as e:
            PrintStyle().error(f"API request failed: {e}")
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make a GET request"""
        return self.request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None) -> requests.Response:
        """Make a POST request"""
        return self.request("POST", endpoint, json_data=json_data)
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None) -> requests.Response:
        """Make a PUT request"""
        return self.request("PUT", endpoint, json_data=json_data)
    
    def patch(self, endpoint: str, json_data: Optional[Dict] = None) -> requests.Response:
        """Make a PATCH request"""
        return self.request("PATCH", endpoint, json_data=json_data)
    
    def delete(self, endpoint: str) -> requests.Response:
        """Make a DELETE request"""
        return self.request("DELETE", endpoint)


class AdversysAPI(Tool):
    """Base tool for Adversys API operations"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_client = AdversysAPIClient()
    
    async def execute(self, **kwargs) -> Response:
        """Execute API operation - to be overridden by subclasses"""
        return Response(
            message="AdversysAPI base tool - this should be overridden",
            break_loop=False
        )
    
    def _handle_api_response(self, resp: requests.Response, success_message: str = "Operation completed successfully") -> Response:
        """Handle API response and return appropriate Tool Response"""
        try:
            resp.raise_for_status()
            data = resp.json() if resp.content else {}
            
            # Format response message
            if isinstance(data, dict):
                message = success_message
                if "message" in data:
                    message = data["message"]
                elif "id" in data:
                    message = f"{success_message}. ID: {data['id']}"
                
                # Include relevant data in message
                if "data" in data:
                    import json
                    message += f"\n\nDetails:\n{json.dumps(data['data'], indent=2)}"
                elif len(data) > 1:
                    import json
                    message += f"\n\nResponse:\n{json.dumps(data, indent=2)}"
            else:
                message = str(data) if data else success_message
            
            return Response(message=message, break_loop=False)
        except requests.HTTPError as e:
            error_msg = f"API request failed with status {resp.status_code}"
            if resp.content:
                try:
                    error_data = resp.json()
                    if "detail" in error_data:
                        error_msg += f": {error_data['detail']}"
                except:
                    error_msg += f": {resp.text[:200]}"
            handle_error(e)
            return Response(message=error_msg, break_loop=False)
        except Exception as e:
            handle_error(e)
            return Response(message=f"Unexpected error: {str(e)}", break_loop=False)
