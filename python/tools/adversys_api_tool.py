"""
CUSTOM ADDITION: Adversys API Client Tool
=========================================
This file is a custom addition to Delta for Adversys Core integration.
It provides a base tool for making authenticated API calls to Adversys Core.

This is NOT part of the upstream Delta codebase.
"""
import os
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
        self.api_token = (
            dotenv.get_dotenv_value("ADVERSYS_API_TOKEN") or 
            os.getenv("ADVERSYS_API_TOKEN") or 
            ""
        )
        
        # Default timeout for requests (in seconds)
        self.timeout = 30
        
        # Cache for the token
        self._token = None
    
    def _get_token(self) -> Optional[str]:
        """Get or obtain API token"""
        # If we have a pre-configured token, use it
        if self.api_token:
            return self.api_token
        
        # If we have a cached token, use it
        if self._token:
            return self._token
        
        # Try to login to get a token
        if self.api_username and self.api_password:
            try:
                login_url = f"{self.base_url}/api/v1/auth/login"
                resp = requests.post(
                    login_url,
                    data={"username": self.api_username, "password": self.api_password},
                    timeout=self.timeout,
                )
                resp.raise_for_status()
                token = (resp.json() or {}).get("access_token")
                if token:
                    self._token = token
                    return token
            except requests.RequestException as e:
                PrintStyle().error(f"Failed to authenticate with Adversys API: {e}")
                return None
        
        return None
    
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
        token = self._get_token()
        
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            resp = requests.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
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
