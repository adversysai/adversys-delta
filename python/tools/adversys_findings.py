"""
CUSTOM ADDITION: Adversys Findings Tool
========================================
This file is a custom addition to Delta for Adversys Core integration.
It provides tools for reviewing and managing findings in Adversys Core.

This is NOT part of the upstream Delta codebase.
"""
import json
from typing import Optional
from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.strings import replace_file_includes
from python.tools.adversys_api_tool import AdversysAPI


class AdversysFindings(AdversysAPI):
    """Tool for managing Adversys findings"""
    
    async def execute(self, **kwargs) -> Response:
        """Execute findings operation"""
        operation = self.args.get("operation", "").lower()
        
        if operation == "create":
            return await self._create_finding()
        elif operation == "list":
            return await self._list_findings()
        elif operation == "get":
            return await self._get_finding()
        elif operation == "update":
            return await self._update_finding()
        elif operation == "update_status":
            # Legacy operation - redirects to update for backward compatibility
            return await self._update_finding()
        elif operation == "summary":
            return await self._get_findings_summary()
        else:
            return Response(
                message=f"Unknown operation: {operation}. Valid operations: create, list, get, update, update_status (deprecated), summary",
                break_loop=False
            )
    
    async def _create_finding(self) -> Response:
        """Create a new finding for a penetration test"""
        test_id = self.args.get("test_id", "")
        target = self.args.get("target", "")
        finding_type = self.args.get("type", "")
        severity = self.args.get("severity", "")
        title = self.args.get("title", "")
        
        if not test_id or not target or not finding_type or not severity or not title:
            return Response(
                message="Missing required parameters: test_id, target, type, severity, and title are required",
                break_loop=False
            )
        
        # Validate severity
        valid_severities = ["critical", "high", "medium", "low", "info"]
        if severity.lower() not in valid_severities:
            return Response(
                message=f"Invalid severity: {severity}. Valid severities: {', '.join(valid_severities)}",
                break_loop=False
            )
        
        # Build finding data
        finding_data = {
            "target": target,
            "type": finding_type,
            "severity": severity.lower(),
            "title": title,
        }
        
        # Optional fields
        # Add Delta attribution to description
        agent_zero_note = "\n\n[Discovered by Delta - Custom Test]"
        
        if "description" in self.args:
            # Process §§include(...) syntax in description
            description = replace_file_includes(self.args["description"])
            # Only append the tag if it's not already present to avoid duplication
            if "[Discovered by Delta - Custom Test]" not in description:
                finding_data["description"] = description + agent_zero_note
            else:
                finding_data["description"] = description
        else:
            finding_data["description"] = agent_zero_note.strip()
        
        if "evidence" in self.args:
            # Process §§include(...) syntax in evidence to replace placeholders with actual file content
            finding_data["evidence"] = replace_file_includes(self.args["evidence"])
        else:
            # If no evidence provided, add a note that this was discovered by Delta
            finding_data["evidence"] = "Finding discovered through Delta custom testing/analysis."
        if "remediation" in self.args:
            finding_data["remediation"] = self.args["remediation"]
        if "cve" in self.args:
            finding_data["cve"] = self.args["cve"]
        if "cvss_score" in self.args:
            try:
                finding_data["cvss_score"] = float(self.args["cvss_score"])
            except (ValueError, TypeError):
                pass
        if "cvss_v3_score" in self.args:
            try:
                finding_data["cvss_v3_score"] = float(self.args["cvss_v3_score"])
            except (ValueError, TypeError):
                pass
        if "cvss_v2_score" in self.args:
            try:
                finding_data["cvss_v2_score"] = float(self.args["cvss_v2_score"])
            except (ValueError, TypeError):
                pass
        if "module_id" in self.args:
            finding_data["module_id"] = self.args["module_id"]
        if "mitre_attack" in self.args:
            # MITRE ATT&CK can be a JSON string or already a dict
            mitre_data = self.args["mitre_attack"]
            if isinstance(mitre_data, str):
                try:
                    finding_data["mitre_attack"] = json.loads(mitre_data)
                except json.JSONDecodeError:
                    return Response(
                        message="Invalid mitre_attack parameter. Expected JSON string or array",
                        break_loop=False
                    )
            else:
                finding_data["mitre_attack"] = mitre_data
        
        resp = self.api_client.post(f"/api/v1/pentests/{test_id}/findings", json_data=finding_data)
        return self._handle_api_response(resp, f"Finding '{title}' created successfully")
    
    async def _list_findings(self) -> Response:
        """List findings with optional filters"""
        test_id = self.args.get("test_id", "")
        severity = self.args.get("severity", "")
        
        params = {}
        if test_id:
            params["penetration_test_id"] = test_id
        if severity:
            params["severity"] = severity
        
        resp = self.api_client.get("/api/v1/findings/", params=params)
        
        try:
            resp.raise_for_status()
            findings = resp.json()
            
            if not findings:
                return Response(message="No findings found", break_loop=False)
            
            # Group by severity
            by_severity = {}
            for finding in findings:
                sev = finding.get('severity', 'unknown')
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(finding)
            
            # Format findings list
            message = f"Found {len(findings)} finding(s):\n\n"
            
            severity_order = ["critical", "high", "medium", "low", "info", "unknown"]
            for sev in severity_order:
                if sev in by_severity:
                    message += f"{sev.upper()} ({len(by_severity[sev])}):\n"
                    for finding in by_severity[sev]:
                        message += f"  - {finding.get('title', 'Unknown')} (ID: {finding.get('id', 'N/A')})\n"
                        message += f"    Target: {finding.get('target', 'N/A')}\n"
                        if finding.get('cve'):
                            message += f"    CVE: {finding.get('cve')}\n"
                    message += "\n"
            
            return Response(message=message.strip(), break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to list findings")
    
    async def _get_finding(self) -> Response:
        """Get finding details"""
        finding_id = self.args.get("finding_id", "")
        
        if not finding_id:
            return Response(
                message="Missing required parameter: finding_id",
                break_loop=False
            )
        
        resp = self.api_client.get(f"/api/v1/findings/{finding_id}")
        
        try:
            resp.raise_for_status()
            finding = resp.json()
            
            message = f"Finding: {finding.get('title', 'Unknown')}\n"
            message += f"ID: {finding.get('id', 'N/A')}\n"
            message += f"Severity: {finding.get('severity', 'N/A')}\n"
            message += f"Status: {finding.get('status', 'N/A')}\n"
            message += f"Target: {finding.get('target', 'N/A')}\n"
            message += f"Type: {finding.get('type', 'N/A')}\n"
            
            if finding.get('cve'):
                message += f"CVE: {finding.get('cve')}\n"
            if finding.get('cvss_score'):
                message += f"CVSS Score: {finding.get('cvss_score')}\n"
            
            message += f"\nDescription:\n{finding.get('description', 'N/A')}\n"
            
            if finding.get('evidence'):
                message += f"\nEvidence:\n{finding.get('evidence')}\n"
            
            if finding.get('remediation'):
                message += f"\nRemediation:\n{finding.get('remediation')}\n"
            
            return Response(message=message, break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to get finding details")
    
    async def _update_finding_status(self) -> Response:
        """Update finding status"""
        finding_id = self.args.get("finding_id", "")
        status = self.args.get("status", "")
        comment = self.args.get("comment", "")
        
        if not finding_id or not status:
            return Response(
                message="Missing required parameters: finding_id and status",
                break_loop=False
            )
        
        # Valid statuses match the Finding model: new, verified, false_positive, remediated
        valid_statuses = ["new", "verified", "false_positive", "remediated"]
        if status not in valid_statuses:
            return Response(
                message=f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}",
                break_loop=False
            )
        
        # Build request data
        request_data = {"status": status}
        if comment:
            # Process §§include(...) syntax in comments
            request_data["comment"] = replace_file_includes(comment)
        
        # Use PATCH method to update finding status
        resp = self.api_client.patch(
            f"/api/v1/findings/{finding_id}",
            json_data=request_data
        )
        
        success_msg = f"Finding status updated to '{status}'"
        if comment:
            success_msg += f" with comment: {comment}"
        
        return self._handle_api_response(resp, success_msg)
    
    async def _update_finding(self) -> Response:
        """Update finding fields (remediation, severity, type, status)
        
        Note: title, description, and evidence are read-only and cannot be updated.
        
        This operation can update one or more fields:
        - remediation: Updated remediation steps
        - severity: Updated severity level (critical, high, medium, low, info)
        - type: Updated finding type (vulnerability, misconfiguration, exposure, information)
        - status: Updated status (new, verified, false_positive, remediated)
        - comment: Optional comment explaining the changes (stored in audit log)
        
        All fields are optional, but at least one must be provided.
        """
        finding_id = self.args.get("finding_id", "")
        
        if not finding_id:
            return Response(
                message="Missing required parameter: finding_id",
                break_loop=False
            )
        
        # Build update data - only include fields that are provided and updatable
        update_data = {}
        
        # Updatable fields
        if "remediation" in self.args:
            # Process §§include(...) syntax in remediation
            update_data["remediation"] = replace_file_includes(self.args["remediation"])
        
        if "severity" in self.args:
            severity = self.args["severity"]
            valid_severities = ["critical", "high", "medium", "low", "info"]
            if severity.lower() not in valid_severities:
                return Response(
                    message=f"Invalid severity: {severity}. Valid severities: {', '.join(valid_severities)}",
                    break_loop=False
                )
            update_data["severity"] = severity.lower()
        
        if "type" in self.args:
            update_data["type"] = self.args["type"]
        
        if "status" in self.args:
            status = self.args["status"]
            valid_statuses = ["new", "verified", "false_positive", "remediated"]
            if status not in valid_statuses:
                return Response(
                    message=f"Invalid status: {status}. Valid statuses: {', '.join(valid_statuses)}",
                    break_loop=False
                )
            update_data["status"] = status
        
        if "comment" in self.args:
            # Process §§include(...) syntax in comments
            # Comment can be empty string to clear it, or a value to set it
            comment = self.args["comment"] if self.args["comment"] else None
            if comment:
                comment = replace_file_includes(comment)
            update_data["comment"] = comment
        
        if not update_data:
            return Response(
                message="No updatable fields provided. Valid fields: remediation, severity, type, status, comment. At least one field must be provided.",
                break_loop=False
            )
        
        # Use PATCH method to update finding
        resp = self.api_client.patch(
            f"/api/v1/findings/{finding_id}",
            json_data=update_data
        )
        
        updated_fields = ", ".join(update_data.keys())
        return self._handle_api_response(resp, f"Finding updated successfully. Updated fields: {updated_fields}")
    
    async def _get_findings_summary(self) -> Response:
        """Get findings summary for a penetration test"""
        test_id = self.args.get("test_id", "")
        
        if not test_id:
            return Response(
                message="Missing required parameter: test_id",
                break_loop=False
            )
        
        resp = self.api_client.get("/api/v1/findings/", params={"penetration_test_id": test_id})
        
        try:
            resp.raise_for_status()
            findings = resp.json()
            
            if not findings:
                return Response(message=f"No findings found for test {test_id}", break_loop=False)
            
            # Count by severity
            severity_counts = {}
            for finding in findings:
                sev = finding.get('severity', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            # Count by status
            status_counts = {}
            for finding in findings:
                status = finding.get('status', 'unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            message = f"Findings Summary for Test {test_id}:\n"
            message += f"Total Findings: {len(findings)}\n\n"
            
            message += "By Severity:\n"
            severity_order = ["critical", "high", "medium", "low", "info"]
            for sev in severity_order:
                if sev in severity_counts:
                    message += f"  {sev.upper()}: {severity_counts[sev]}\n"
            
            message += "\nBy Status:\n"
            for status, count in status_counts.items():
                message += f"  {status}: {count}\n"
            
            return Response(message=message, break_loop=False)
        except Exception as e:
            return self._handle_api_response(resp, "Failed to get findings summary")
