# adversys_findings Tool

> **CUSTOM ADDITION**: This file is a custom addition to the Delta repository. It documents the Adversys Core integration tool that is NOT part of the upstream Delta codebase.

Tool for reviewing and managing security findings in Adversys Core.

## Operations

### create
Create a new finding for a penetration test. Use this when you perform custom tests or manual analysis and discover vulnerabilities.

**Note:** Findings created through this tool are automatically marked as "[Discovered by Delta - Custom Test]" in the description, making them easily identifiable.

**Parameters:**
- `operation`: "create"
- `test_id` (required): UUID of the penetration test
- `target` (required): Target where the finding was discovered (IP, domain, hostname, etc.)
- `type` (required): Finding type - "vulnerability", "misconfiguration", "exposure", or other
- `severity` (required): Severity level - "critical", "high", "medium", "low", "info"
- `title` (required): Brief title describing the finding
- `description` (optional): Detailed description of the finding (Delta attribution will be added automatically)
- `evidence` (optional): Evidence or proof of the finding (command output, screenshots, etc.)
- `remediation` (optional): Recommended remediation steps
- `cve` (optional): CVE identifier if applicable (e.g., "CVE-2024-1234")
- `cvss_score` (optional): CVSS score (float)
- `cvss_v3_score` (optional): CVSS v3.1 score (float)
- `cvss_v2_score` (optional): CVSS v2.0 score (float)
- `module_id` (optional): ID of the module that discovered this
- `mitre_attack` (optional): JSON array of MITRE ATT&CK techniques: `[{"technique_id": "T1190", "name": "Exploit Public-Facing Application"}]`

**Example:**
```
operation: create
test_id: "test-uuid"
target: "192.168.1.100"
type: "vulnerability"
severity: "high"
title: "Open SSH port with weak authentication"
description: "SSH service is accessible and accepts weak passwords"
evidence: "nmap scan showed port 22 open, manual testing confirmed weak password acceptance"
remediation: "Implement strong password policy and consider key-based authentication"
```

**Finding Identification:**
- All findings created through this tool will have "[Discovered by Delta - Custom Test]" appended to the description
- This allows you to easily filter or identify findings discovered by Delta vs. automated tests

### list
List findings with optional filters.

**Parameters:**
- `operation`: "list"
- `test_id` (optional): Filter by penetration test UUID
- `severity` (optional): Filter by severity - "critical", "high", "medium", "low", "info"

**Returns:**
- List of findings grouped by severity
- Finding title, ID, target, and CVE (if applicable)

### get
Get detailed information about a specific finding.

**Parameters:**
- `operation`: "get"
- `finding_id` (required): UUID of the finding

**Returns:**
- Full finding details including:
  - Title, description, severity, status
  - Target, type, CVE, CVSS scores
  - Evidence and remediation recommendations

### update
Update finding fields. Use this to modify remediation steps, severity, type, or status of an existing finding.

**Note:** The `update_status` operation is deprecated. Use `update` instead, which provides the same functionality plus the ability to update other fields.

**Important:** The following fields are **read-only** and cannot be updated:
- `title`: Cannot be changed after creation
- `description`: Cannot be changed after creation
- `evidence`: Cannot be changed after creation

**Parameters:**
- `operation`: "update"
- `finding_id` (required): UUID of the finding to update
- `remediation` (optional): Updated remediation steps (use for "how to fix" guidance)
- `severity` (optional): Updated severity - "critical", "high", "medium", "low", "info"
- `type` (optional): Updated type - "vulnerability", "misconfiguration", "exposure", "information"
- `status` (optional): Updated status - "new", "verified", "false_positive", "remediated"
- `comment` (optional): Comment explaining status changes or other notes (stored directly on the finding, visible in UI)

**Note:** At least one field (remediation, severity, type, status, or comment) must be provided.

**Examples:**

Update only status:
```
operation: update
finding_id: "9ae0040c-d770-4a96-95fd-51d8e3a12909"
status: "false_positive"
comment: "URL redirects to Amazon Cognito login page instead of exposing sensitive content. This is a false positive as the file is protected by authentication."
```

Update multiple fields:
```
operation: update
finding_id: "9ae0040c-d770-4a96-95fd-51d8e3a12909"
remediation: "Update the application to version 2.0.1 which patches this vulnerability. Also implement rate limiting."
severity: "high"
status: "verified"
comment: "Updated remediation based on vendor security advisory and verified the vulnerability"
```

**Use Cases:**
- **Update status only:** Mark findings as `false_positive`, `verified`, or `remediated`. Always include a `comment` when marking as `false_positive` to document why (e.g., "URL redirects to login page", "Requires authentication", "False positive - expected behavior").
- **Update remediation:** When better solutions are found or more details are available. Use `remediation` for "how to fix" guidance.
- **Adjust severity:** If initial assessment was incorrect
- **Change type:** If classification was wrong
- **Update multiple fields:** Update status along with remediation, severity, or type in a single operation

**Comment vs Remediation:**
- **Use `comment`** for: Status change explanations (especially false positives), notes about why something was changed, general observations
- **Use `remediation`** for: Step-by-step instructions on how to fix the vulnerability, technical remediation guidance

**Best Practice:** 
- Always include a `comment` when marking findings as `false_positive` to document why the finding is not a real vulnerability. The comment is stored directly on the finding and is visible in the UI.
- Use `remediation` for actual fix instructions, not for explaining false positives.

### summary
Get a summary of findings for a penetration test.

**Parameters:**
- `operation`: "summary"
- `test_id` (required): UUID of the penetration test

**Returns:**
- Total findings count
- Breakdown by severity
- Breakdown by status
