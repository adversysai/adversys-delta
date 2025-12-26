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

**Parameters:**
- `operation`: "search"
- `query` (optional): Search in target value (e.g., "adversys.ai")
- `name` (optional): Search in target name
- `type` (optional): Filter by target type ("domain", "ip_address", "cidr", etc.)

**Example:**
```
operation: search
query: "adversys.ai"
```

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
