# adversys_analysis Tool

> **CUSTOM ADDITION**: This file is a custom addition to the Delta repository. It documents the Adversys Core integration tool that is NOT part of the upstream Delta codebase.

Tool for analyzing targets and providing security insights in Adversys Core.

## Operations

### analyze_target
Comprehensive analysis of a target.

**Parameters:**
- `operation`: "analyze_target"
- `target_id` (required): UUID of the target

**Returns:**
- Target information
- Number of penetration tests
- Total findings count
- Findings breakdown by severity
- Critical/high findings summary
- Recent penetration test activity

### get_vulnerabilities
Get all vulnerabilities for a target (excludes info findings).

**Parameters:**
- `operation`: "get_vulnerabilities"
- `target_id` (required): UUID of the target

**Returns:**
- List of vulnerabilities grouped by severity
- CVE information where available

### get_findings
Get all findings (including info) for a target.

**Parameters:**
- `operation`: "get_findings"
- `target_id` (required): UUID of the target

**Returns:**
- Complete list of findings for the target
- Finding details including severity, status, and CVE

## Use Cases

- **Pre-test Analysis**: Analyze a target before creating a penetration test to understand existing security posture
- **Post-test Review**: Analyze findings after test completion to prioritize remediation
- **Ongoing Monitoring**: Track security status of targets over time
