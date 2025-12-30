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
        self.api_username = (
            dotenv.get_dotenv_value("ADVERSYS_API_USERNAME") or 
            os.getenv("ADVERSYS_API_USERNAME") or 
            "orchestrator-service"
        )
        self.api_password = (
            dotenv.get_dotenv_value("ADVERSYS_API_PASSWORD") or 
            os.getenv("ADVERSYS_API_PASSWORD") or 
            ""
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
        
        # Session for cookie-based auth
        self.session = requests.Session()
        self.session.verify = self.verify_ssl
        self.csrf_token: Optional[str] = None
        self.auth_backoff_until = 0.0
    
    def _ensure_session(self) -> bool:
        """Ensure we have a valid session cookie by logging in if needed."""
        if not self.api_username or not self.api_password:
            return False
        
        # Check if we have a session cookie and it's likely still valid
        # We'll validate it by making a test request if we're unsure
        session_cookie = self.session.cookies.get("adversys_session")
        if session_cookie:
            if not self.csrf_token:
                self.csrf_token = self.session.cookies.get("adversys_csrf")
            # Cookie exists - assume it's valid (will be validated on first API call)
            return True
        
        # No session cookie, need to login
        if time.time() < self.auth_backoff_until:
            return False

        try:
            login_url = f"{self.base_url}/api/v1/auth/login"
            resp = self.session.post(
                login_url,
                json={"username": self.api_username, "password": self.api_password},
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            if resp.status_code == 429:
                # Rate limited - back off for longer to avoid hitting limit again
                self.auth_backoff_until = time.time() + 300  # 5 minutes (matches API rate limit window)
                PrintStyle().error("Auth rate-limited (429). Backing off for 5 minutes before retrying.")
                return False
            resp.raise_for_status()
            self.csrf_token = self.session.cookies.get("adversys_csrf")
            return True
        except requests.RequestException as e:
            # Back off for 30 seconds on other errors
            self.auth_backoff_until = time.time() + 30
            PrintStyle().error(f"Failed to authenticate with Adversys API: {e}")
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
        self._ensure_session()
        headers = {"Content-Type": "application/json"}
        if method.upper() in ("POST", "PUT", "PATCH", "DELETE"):
            if not self.csrf_token:
                self.csrf_token = self.session.cookies.get("adversys_csrf")
            if self.csrf_token:
                headers["X-CSRF-Token"] = self.csrf_token
        
        try:
            resp = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            if resp.status_code == 401:
                # Retry once after re-auth - clear cookies and force re-login
                # Only retry if we're not rate-limited
                if time.time() >= self.auth_backoff_until:
                    self.session.cookies.clear()
                    self.csrf_token = None
                    if self._ensure_session():
                        # Update CSRF token in headers for retry
                        if method.upper() in ("POST", "PUT", "PATCH", "DELETE") and self.csrf_token:
                            headers["X-CSRF-Token"] = self.csrf_token
                        resp = self.session.request(
                            method=method,
                            url=url,
                            json=json_data,
                            params=params,
                            headers=headers,
                            timeout=self.timeout,
                            verify=self.verify_ssl,
                        )
                else:
                    # Rate limited - don't retry, just return the 401
                    PrintStyle().warning("Skipping 401 retry due to rate limiting backoff period.")
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
