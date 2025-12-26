# Branding Patch Script

> **CUSTOM ADDITION**: This file and the `apply-branding.sh` script are custom additions to the Delta repository. They are not part of the upstream Delta codebase and are used to rebrand the application to "Delta" during the Docker build process.

## Overview

The `apply-branding.sh` script automatically rebrands the application from "Delta" to "Delta" during the Docker build process. This allows us to maintain the upstream Delta repository while applying our own branding.

## What It Does

The script replaces user-facing text in the following file types:

- **HTML files**: Titles, headings, alt text, and visible text
- **JavaScript files**: User-facing strings in quotes, template literals, and comments
- **JSON files**: Manifest files and configuration (names, descriptions)
- **Python files**: User-facing messages, docstrings, and comments
- **Markdown files**: Documentation and README files (excluding knowledge base)

**Replacement patterns:**
- `Delta` → `Delta`
- `Delta` → `Delta`
- `Delta Chat` → `Delta Chat`
- `A0 MCP` → `Delta MCP`
- `A0 A2A` → `Delta A2A`
- `delta.ai` → `delta.ai`
- `Deltaai/agent-zero` → `deltaai/delta`

## What It Preserves

The script is designed to **NOT** break technical functionality:

- Variable names (e.g., `agentZero`, `agent_zero`)
- File paths (e.g., `/a0`, `/git/agent-zero`)
- Technical references in code
- Knowledge base files (to preserve technical accuracy)
- Vendor/third-party files

## Usage

The script is automatically run during the Docker build process in both:
- `Dockerfile` (production builds)
- `DockerfileLocal` (local development builds)

It runs **before** the installation scripts, ensuring all user-facing text is rebranded before the application is installed.

## Manual Execution

If you need to run the script manually (e.g., for testing):

```bash
chmod +x scripts/apply-branding.sh
./scripts/apply-branding.sh /path/to/agent-zero
```

Or from within a container:

```bash
/git/agent-zero/scripts/apply-branding.sh /git/agent-zero
```

## Customization

To change the branding (e.g., from "Delta" to another name), edit the `apply-branding.sh` script and update the replacement patterns:

- `Delta` → Your brand name
- `Delta` → Your brand name (abbreviation)
- `Delta Chat` → Your brand name Chat
- `delta.ai` → Your domain
- `Deltaai/agent-zero` → Your GitHub org/repo

## Maintenance

When updating from upstream Delta:

1. Pull the latest changes from the upstream repository
2. Rebuild the Docker image - the branding script will automatically apply
3. Test to ensure all user-facing text shows your branding
4. Verify technical functionality still works (paths, variables, etc.)

## Files Modified

The script modifies files in:
- `webui/` - All HTML, JS, JSON files
- `python/` - Python source files (excluding vendor)
- `docs/` - Documentation files (excluding knowledge base)
- `prompts/` - Prompt files

## Notes

- The script uses `sed` for in-place file editing
- It's designed to be idempotent (safe to run multiple times)
- Errors are logged but don't stop the build (uses `|| echo` fallback)
- The script preserves file permissions and structure

