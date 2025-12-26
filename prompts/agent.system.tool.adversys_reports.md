# adversys_reports Tool

> **CUSTOM ADDITION**: This file is a custom addition to the Delta repository. It documents the Adversys Core integration tool that is NOT part of the upstream Delta codebase.

Tool for generating penetration test reports in Adversys Core.

## Operations

### generate
Generate a penetration test report.

**Parameters:**
- `operation`: "generate"
- `test_id` (required): UUID of the penetration test
- `format` (optional): "html" (default) or "pdf"

**Returns:**
- Report generation confirmation
- Report size/length information

### download
Download a penetration test report.

**Parameters:**
- `operation`: "download"
- `test_id` (required): UUID of the penetration test
- `format` (optional): "html" (default) or "pdf"

**Returns:**
- Report content (HTML) or download information (PDF)
- Content-Disposition header information

## Notes

- Reports are generated from completed penetration tests
- HTML reports can be viewed directly in a browser
- PDF reports are binary files suitable for sharing and archival
- Reports include findings, artifacts, execution details, and recommendations
