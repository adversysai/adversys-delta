"""
Adversys Reports Tool
Tool for generating penetration test reports in Adversys Core
"""
import json
from typing import Optional
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.tools.adversys_api_tool import AdversysAPI


class AdversysReports(AdversysAPI):
    """Tool for generating Adversys reports"""
    
    async def execute(self, **kwargs) -> Response:
        """Execute report operation"""
        operation = self.args.get("operation", "").lower()
        
        if operation == "generate":
            return await self._generate_report()
        elif operation == "download":
            return await self._download_report()
        else:
            return Response(
                message=f"Unknown operation: {operation}. Valid operations: generate, download",
                break_loop=False
            )
    
    async def _generate_report(self) -> Response:
        """Generate a penetration test report"""
        test_id = self.args.get("test_id", "")
        format_type = self.args.get("format", "html").lower()
        
        if not test_id:
            return Response(
                message="Missing required parameter: test_id",
                break_loop=False
            )
        
        if format_type not in ["html", "pdf"]:
            return Response(
                message=f"Invalid format: {format_type}. Valid formats: html, pdf",
                break_loop=False
            )
        
        params = {"format": format_type}
        resp = self.api_client.get(f"/api/v1/pentests/{test_id}/report", params=params)
        
        try:
            resp.raise_for_status()
            
            if format_type == "html":
                html_content = resp.text
                # Return a summary message with report info
                message = f"HTML report generated for test {test_id}\n"
                message += f"Report length: {len(html_content)} characters\n"
                message += f"\nTo view the full report, use the download operation or access it via the API."
                return Response(message=message, break_loop=False)
            else:
                # PDF - return info about the binary
                message = f"PDF report generated for test {test_id}\n"
                message += f"Report size: {len(resp.content)} bytes\n"
                message += f"\nTo download the report, use the download operation or access it via the API."
                return Response(message=message, break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to generate report")
    
    async def _download_report(self) -> Response:
        """Download a penetration test report"""
        test_id = self.args.get("test_id", "")
        format_type = self.args.get("format", "html").lower()
        
        if not test_id:
            return Response(
                message="Missing required parameter: test_id",
                break_loop=False
            )
        
        if format_type not in ["html", "pdf"]:
            return Response(
                message=f"Invalid format: {format_type}. Valid formats: html, pdf",
                break_loop=False
            )
        
        params = {"format": format_type, "download": "true"}
        resp = self.api_client.get(f"/api/v1/pentests/{test_id}/report", params=params)
        
        try:
            resp.raise_for_status()
            
            if format_type == "html":
                message = f"HTML report downloaded for test {test_id}\n"
                message += f"Content-Disposition: {resp.headers.get('Content-Disposition', 'N/A')}\n"
                message += f"\nReport content (first 1000 chars):\n{resp.text[:1000]}..."
            else:
                message = f"PDF report downloaded for test {test_id}\n"
                message += f"Content-Disposition: {resp.headers.get('Content-Disposition', 'N/A')}\n"
                message += f"Report size: {len(resp.content)} bytes\n"
                message += f"\nNote: PDF content is binary and cannot be displayed here."
            
            return Response(message=message, break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to download report")
