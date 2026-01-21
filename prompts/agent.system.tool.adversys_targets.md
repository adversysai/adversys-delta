# adversys_targets Tool

> **CUSTOM ADDITION**: This file is a custom addition to the Delta repository. It documents the Adversys Core integration tool that is NOT part of the upstream Delta codebase.

Tool for managing penetration testing targets in Adversys Core.

## Operations

### create
Create a new target for penetration testing.

**Parameters:**
- `operation`: "create"
- `name` (required): Name for the target
- `type` (required): Target type - "ip_address", "ip_range", "domain", "hostname", or "cidr"
- `value` (required): Target value (e.g., "192.168.1.1" or "192.168.1.0/24")
- `description` (optional): Description of the target
- `values` (optional): JSON array of multiple target values: `[{"type": "ip_address", "value": "1.2.3.4"}, ...]`

**Example:**
```
operation: create
name: "Internal Network"
type: "cidr"
value: "192.168.1.0/24"
description: "Internal corporate network segment"
```

### list
List all available targets.

**Parameters:**
- `operation`: "list"

### search
Search for targets by value, name, or type.

**IMPORTANT**: The search operation searches in both the target **name** and **value** (IP address) fields. For example, searching for "192.168.10.10" will find targets with that IP address, and searching for "GOAD-DC01" will find targets with that name.

**Parameters:**
- `operation`: "search"
- `query` (optional): Search in both target name and value (IP address). For example, "192.168.10.10" or "GOAD-DC01"
- `name` (optional): Search specifically in target name
- `type` (optional): Filter by target type ("domain", "ip_address", "cidr", etc.)

**Example:**
```
operation: search
query: "192.168.10.10"
```
This will find targets where the name or IP address contains "192.168.10.10".

### get
Get detailed information about a specific target.

**Parameters:**
- `operation`: "get"
- `target_id` (required): UUID of the target

### update
Update an existing target.

**Parameters:**
- `operation`: "update"
- `target_id` (required): UUID of the target
- `name` (optional): New name
- `description` (optional): New description
- `type` and `value` (optional): Update target type/value
- `values` (optional): JSON array for multiple values

### delete
Delete a target.

**Parameters:**
- `operation`: "delete"
- `target_id` (required): UUID of the target
