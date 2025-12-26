"""
Adversys Analysis Tool
Tool for analyzing targets and providing insights in Adversys Core
"""
import json
from typing import Optional
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.tools.adversys_api_tool import AdversysAPI


class AdversysAnalysis(AdversysAPI):
    """Tool for analyzing Adversys targets"""
    
    async def execute(self, **kwargs) -> Response:
        """Execute analysis operation"""
        operation = self.args.get("operation", "").lower()
        
        if operation == "analyze_target":
            return await self._analyze_target()
        elif operation == "get_vulnerabilities":
            return await self._get_target_vulnerabilities()
        elif operation == "get_findings":
            return await self._get_target_findings()
        else:
            return Response(
                message=f"Unknown operation: {operation}. Valid operations: analyze_target, get_vulnerabilities, get_findings",
                break_loop=False
            )
    
    async def _analyze_target(self) -> Response:
        """Analyze a target and provide insights"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        # Get target details
        target_resp = self.api_client.get(f"/api/v1/targets/{target_id}")
        
        try:
            target_resp.raise_for_status()
            target = target_resp.json()
        except:
            return Response(
                message=f"Failed to retrieve target {target_id}",
                break_loop=False
            )
        
        # Get all findings for this target
        findings_resp = self.api_client.get("/api/v1/findings/", params={"target": target.get("value", "")})
        
        # Get all penetration tests for this target
        pentests_resp = self.api_client.get("/api/v1/pentests/")
        
        try:
            findings = findings_resp.json() if findings_resp.status_code == 200 else []
            pentests = pentests_resp.json() if pentests_resp.status_code == 200 else []
            
            # Filter pentests for this target
            target_pentests = [pt for pt in pentests if pt.get("target_id") == target_id]
        except:
            findings = []
            target_pentests = []
        
        # Build analysis message
        message = f"Target Analysis: {target.get('name', 'Unknown')}\n"
        message += f"ID: {target.get('id', 'N/A')}\n"
        message += f"Type: {target.get('type', 'N/A')}\n"
        message += f"Value: {target.get('value', 'N/A')}\n"
        
        if target.get('description'):
            message += f"Description: {target.get('description')}\n"
        
        message += f"\n--- Analysis ---\n"
        message += f"Penetration Tests: {len(target_pentests)}\n"
        message += f"Total Findings: {len(findings)}\n"
        
        if findings:
            # Count by severity
            severity_counts = {}
            for finding in findings:
                sev = finding.get('severity', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            message += "\nFindings by Severity:\n"
            severity_order = ["critical", "high", "medium", "low", "info"]
            for sev in severity_order:
                if sev in severity_counts:
                    message += f"  {sev.upper()}: {severity_counts[sev]}\n"
            
            # List critical and high findings
            critical_high = [f for f in findings if f.get('severity') in ['critical', 'high']]
            if critical_high:
                message += f"\n⚠️ Critical/High Findings ({len(critical_high)}):\n"
                for finding in critical_high[:5]:  # Limit to first 5
                    message += f"  - {finding.get('title', 'Unknown')} ({finding.get('severity', 'N/A')})\n"
                if len(critical_high) > 5:
                    message += f"  ... and {len(critical_high) - 5} more\n"
        
        if target_pentests:
            message += f"\nRecent Penetration Tests:\n"
            for pt in target_pentests[:3]:  # Show last 3
                message += f"  - {pt.get('name', 'Unknown')} ({pt.get('status', 'N/A')}) - {pt.get('progress_percent', 0)}% complete\n"
        
        return Response(message=message, break_loop=False)
    
    async def _get_target_vulnerabilities(self) -> Response:
        """Get vulnerabilities for a target"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        # Get target to find its value
        target_resp = self.api_client.get(f"/api/v1/targets/{target_id}")
        
        try:
            target_resp.raise_for_status()
            target = target_resp.json()
        except:
            return Response(
                message=f"Failed to retrieve target {target_id}",
                break_loop=False
            )
        
        # Get findings for this target
        findings_resp = self.api_client.get("/api/v1/findings/", params={"target": target.get("value", "")})
        
        try:
            findings_resp.raise_for_status()
            findings = findings_resp.json()
            
            # Filter to only vulnerabilities (not info findings)
            vulnerabilities = [f for f in findings if f.get('severity') not in ['info', 'unknown']]
            
            if not vulnerabilities:
                return Response(message=f"No vulnerabilities found for target {target_id}", break_loop=False)
            
            message = f"Vulnerabilities for Target: {target.get('name', 'Unknown')}\n"
            message += f"Total: {len(vulnerabilities)}\n\n"
            
            # Group by severity
            by_severity = {}
            for vuln in vulnerabilities:
                sev = vuln.get('severity', 'unknown')
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(vuln)
            
            severity_order = ["critical", "high", "medium", "low"]
            for sev in severity_order:
                if sev in by_severity:
                    message += f"{sev.upper()} ({len(by_severity[sev])}):\n"
                    for vuln in by_severity[sev]:
                        message += f"  - {vuln.get('title', 'Unknown')}\n"
                        if vuln.get('cve'):
                            message += f"    CVE: {vuln.get('cve')}\n"
                    message += "\n"
            
            return Response(message=message.strip(), break_loop=False)
        except Exception as e:
            return self._handle_api_response(findings_resp, "Failed to get target vulnerabilities")
    
    async def _get_target_findings(self) -> Response:
        """Get all findings for a target"""
        target_id = self.args.get("target_id", "")
        
        if not target_id:
            return Response(
                message="Missing required parameter: target_id",
                break_loop=False
            )
        
        # Get target to find its value
        target_resp = self.api_client.get(f"/api/v1/targets/{target_id}")
        
        try:
            target_resp.raise_for_status()
            target = target_resp.json()
        except:
            return Response(
                message=f"Failed to retrieve target {target_id}",
                break_loop=False
            )
        
        # Get findings for this target
        findings_resp = self.api_client.get("/api/v1/findings/", params={"target": target.get("value", "")})
        
        try:
            findings_resp.raise_for_status()
            findings = findings_resp.json()
            
            if not findings:
                return Response(message=f"No findings found for target {target_id}", break_loop=False)
            
            message = f"All Findings for Target: {target.get('name', 'Unknown')}\n"
            message += f"Total: {len(findings)}\n\n"
            
            for finding in findings:
                message += f"- {finding.get('title', 'Unknown')} ({finding.get('severity', 'N/A')})\n"
                message += f"  Status: {finding.get('status', 'N/A')}\n"
                if finding.get('cve'):
                    message += f"  CVE: {finding.get('cve')}\n"
                message += "\n"
            
            return Response(message=message.strip(), break_loop=False)
        except Exception as e:
            return self._handle_api_response(findings_resp, "Failed to get target findings")
