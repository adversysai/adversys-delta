# Delta - Adversys Core Integration Guide

> **CUSTOM ADDITION**: This document is a custom addition to the Delta repository. It documents the Adversys Core integration features that are NOT part of the upstream Delta codebase.

This document explains how Delta interacts with Adversys Core functionalities.

## Architecture Overview

Delta integrates with Adversys Core through a set of specialized tools that make authenticated HTTP API calls to the Adversys API service. The integration is designed to allow Delta to assist users with penetration testing workflows.

## Configuration

### Environment Variables

Delta connects to Adversys Core using the following environment variables (configured in `docker-compose.yml`):

- **`ADVERSYS_API_URL`**: Base URL for the Adversys API (default: `http://api:8000`)
- **`ADVERSYS_API_USERNAME`**: Service account username (default: `orchestrator-service`)
- **`ADVERSYS_API_PASSWORD`**: Service account password
- **`ADVERSYS_API_TOKEN`**: Optional pre-configured API token (if provided, skips login)

### Authentication

The integration uses Bearer token authentication:

1. **Token-based**: If `ADVERSYS_API_TOKEN` is set, it's used directly
2. **Username/Password**: If no token is provided, the client logs in via `/api/v1/auth/login` to obtain a token
3. **Token Caching**: Tokens are cached in memory to avoid repeated logins

## Core Components

### 1. AdversysAPIClient (`python/tools/adversys_api_tool.py`)

Base HTTP client that handles:
- Configuration from environment variables
- Authentication (token retrieval and caching)
- HTTP request methods (GET, POST, PUT, DELETE)
- Error handling and response formatting

**Key Methods:**
- `_get_token()`: Obtains authentication token
- `request()`: Makes authenticated API requests
- `get()`, `post()`, `put()`, `delete()`: Convenience methods

### 2. AdversysAPI Base Tool (`python/tools/adversys_api_tool.py`)

Base class for all Adversys tools that provides:
- API client initialization
- Standardized response handling
- Error formatting

### 3. Specialized Tools

All tools inherit from `AdversysAPI` and implement operation-based interfaces:

#### `adversys_targets` - Target Management
- **Operations**: `create`, `list`, `get`, `update`, `delete`
- **Endpoints**: `/api/v1/targets/`
- **Purpose**: Manage penetration testing targets (IPs, domains, ranges, etc.)

#### `adversys_pentests` - Penetration Test Management
- **Operations**: `create`, `start`, `status`, `pause`, `resume`, `approve_exploit`, `list`
- **Endpoints**: `/api/v1/pentests/`
- **Purpose**: Create, execute, and manage penetration tests

#### `adversys_findings` - Findings Management
- **Operations**: `list`, `get`, `update_status`, `summary`
- **Endpoints**: `/api/v1/findings/`
- **Purpose**: Review and manage security findings from tests

#### `adversys_reports` - Report Generation
- **Operations**: `generate`, `download`
- **Endpoints**: `/api/v1/reports/`
- **Purpose**: Generate HTML/PDF reports for completed tests

#### `adversys_analysis` - Target Analysis
- **Operations**: `analyze_target`, `get_vulnerabilities`, `get_findings_for_target`
- **Endpoints**: `/api/v1/analysis/`
- **Purpose**: Analyze targets and retrieve security insights

## Usage Pattern

### Standard Workflow

1. **Create Target**
   ```python
   adversys_targets(
       operation="create",
       name="Web Server",
       type="ip_address",
       value="192.168.1.100"
   )
   ```

2. **Create Penetration Test**
   ```python
   adversys_pentests(
       operation="create",
       name="Initial Scan",
       target_id="target-uuid",
       test_type="black_box"
   )
   ```

3. **Start Test**
   ```python
   adversys_pentests(
       operation="start",
       test_id="test-uuid"
   )
   ```

4. **Monitor Progress**
   ```python
   adversys_pentests(
       operation="status",
       test_id="test-uuid"
   )
   ```

5. **Review Findings**
   ```python
   adversys_findings(
       operation="list",
       test_id="test-uuid",
       severity="critical"
   )
   ```

6. **Generate Report**
   ```python
   adversys_reports(
       operation="generate",
       test_id="test-uuid",
       format="html"
   )
   ```

## Implementation Details

### Tool Structure

Each tool follows this pattern:

```python
class AdversysTool(AdversysAPI):
    async def execute(self, **kwargs) -> Response:
        operation = self.args.get("operation", "").lower()
        
        if operation == "create":
            return await self._create()
        elif operation == "list":
            return await self._list()
        # ... other operations
        
    async def _create(self) -> Response:
        # Validate parameters
        # Build request data
        # Make API call
        resp = self.api_client.post("/api/v1/endpoint/", json_data=data)
        return self._handle_api_response(resp, "Success message")
```

### Response Handling

The `_handle_api_response()` method:
- Checks HTTP status codes
- Parses JSON responses
- Formats user-friendly messages
- Handles errors gracefully
- Returns standardized `Response` objects

### Error Handling

Errors are handled at multiple levels:
1. **Network errors**: Caught and reported with connection details
2. **HTTP errors**: Status codes and error messages from API
3. **Validation errors**: Missing or invalid parameters
4. **Unexpected errors**: Generic error messages with details

## System Prompt Integration

Delta is configured with a specialized system prompt (`prompts/adversys/agent.system.md`) that:
- Explains the role in Adversys Core
- Documents all available tools and operations
- Provides usage examples
- Outlines best practices
- Defines standard workflows

## API Endpoints Used

All tools interact with the Adversys API at these endpoints:

- `/api/v1/auth/login` - Authentication
- `/api/v1/targets/` - Target management
- `/api/v1/pentests/` - Penetration test management
- `/api/v1/findings/` - Findings management
- `/api/v1/reports/` - Report generation
- `/api/v1/analysis/` - Target analysis

## Network Configuration

In Docker Compose:
- Delta connects to the API service via the `adversys-network`
- Service name resolution: `http://api:8000`
- All services are on the same Docker network for internal communication

## Security Considerations

1. **Authentication**: All requests use Bearer token authentication
2. **Credentials**: Stored in environment variables, not in code
3. **Token Caching**: Tokens cached in memory (not persisted)
4. **Error Messages**: Sensitive information filtered from error responses
5. **ROE Compliance**: Tools respect Rules of Engagement when executing tests

## Troubleshooting

### Common Issues

1. **Authentication Failures**
   - Check `ADVERSYS_API_USERNAME` and `ADVERSYS_API_PASSWORD`
   - Verify API service is running and accessible
   - Check network connectivity between containers

2. **Connection Errors**
   - Verify `ADVERSYS_API_URL` is correct
   - Ensure services are on the same Docker network
   - Check API service health endpoint

3. **Invalid Parameters**
   - Review tool documentation for required parameters
   - Check parameter types (strings, JSON, etc.)
   - Verify IDs are valid UUIDs

## Future Enhancements

Potential improvements:
- WebSocket support for real-time test progress
- Batch operations for multiple targets
- Advanced filtering and search capabilities
- Integration with other Adversys Core modules
- Caching layer for frequently accessed data
