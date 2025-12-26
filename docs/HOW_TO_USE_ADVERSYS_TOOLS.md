# How to Prompt Delta to Use Adversys Core Tools

> **CUSTOM ADDITION**: This document is a custom addition to the Delta repository. It documents the Adversys Core integration tools that are NOT part of the upstream Delta codebase.

Delta automatically discovers and has access to all Adversys Core tools. You don't need to explicitly call the tools - just ask the agent in natural language, and it will use the appropriate tools based on your request.

## How Tool Discovery Works

1. **Automatic Discovery**: Delta automatically discovers all tools in `python/tools/` directory
2. **Tool Documentation**: Each tool has a markdown file in `prompts/adversys/agent.system.tool.*.md` that describes how to use it
3. **System Prompt**: The tool documentation is automatically injected into the agent's system prompt via the `{{tools}}` placeholder
4. **Natural Language**: The agent understands natural language requests and translates them into tool calls

## Simple Examples

### Creating a Target

**You say:**
```
"Create a target for 192.168.1.100 called 'Web Server'"
```

**Delta will:**
- Recognize this requires the `adversys_targets` tool
- Use `operation="create"` with the appropriate parameters
- Execute the tool and report back

### Starting a Penetration Test

**You say:**
```
"Start a penetration test for target abc-123 called 'Initial Scan'"
```

**Delta will:**
- First create the penetration test (if needed)
- Then start it using `adversys_pentests` with `operation="start"`

### Checking Findings

**You say:**
```
"Show me all critical findings from the latest test"
```

**Delta will:**
- Use `adversys_findings` with `operation="list"` and `severity="critical"`

## More Detailed Examples

### Complete Workflow Example

**You say:**
```
"I want to test the internal network 192.168.1.0/24. 
Create a target, set up a black box penetration test, 
start it, and then show me the findings when it's done."
```

**Delta will:**
1. Create target using `adversys_targets` (operation: create)
2. Create penetration test using `adversys_pentests` (operation: create)
3. Start the test using `adversys_pentests` (operation: start)
4. Monitor progress using `adversys_pentests` (operation: status)
5. List findings using `adversys_findings` (operation: list)

### Specific Operations

If you need a specific operation, you can be more explicit:

**You say:**
```
"List all available targets"
```
→ Uses `adversys_targets` with `operation="list"`

**You say:**
```
"Get the status of penetration test abc-123"
```
→ Uses `adversys_pentests` with `operation="status"` and `test_id="abc-123"`

**You say:**
```
"Generate an HTML report for test xyz-789"
```
→ Uses `adversys_reports` with `operation="generate"`, `test_id="xyz-789"`, `format="html"`

## Available Tools and Common Prompts

### adversys_targets

**Common prompts:**
- "Create a target for [IP/domain]"
- "List all targets"
- "Show me target [target_id]"
- "Update target [target_id]"
- "Delete target [target_id]"

### adversys_pentests

**Common prompts:**
- "Create a penetration test for target [target_id]"
- "Start penetration test [test_id]"
- "What's the status of test [test_id]?"
- "Pause test [test_id]"
- "Resume test [test_id]"
- "Approve the exploit for test [test_id]"
- "List all penetration tests"

### adversys_findings

**Common prompts:**
- "Show me findings from test [test_id]"
- "List all critical findings"
- "Get details for finding [finding_id]"
- "Update finding [finding_id] status to confirmed"
- "Give me a summary of findings for test [test_id]"

### adversys_reports

**Common prompts:**
- "Generate a report for test [test_id]"
- "Create an HTML report for test [test_id]"
- "Generate a PDF report for test [test_id]"
- "Download the report for test [test_id]"

### adversys_analysis

**Common prompts:**
- "Analyze target [target_id]"
- "Show me vulnerabilities for target [target_id]"
- "Get all findings for target [target_id]"

## Tips for Effective Prompts

### 1. Be Specific
✅ **Good**: "Create a target for 192.168.1.100 called 'Production Web Server'"
❌ **Vague**: "Make a target"

### 2. Provide Context
✅ **Good**: "Start a black box penetration test for the target I just created"
❌ **Unclear**: "Start a test"

### 3. Use Natural Language
✅ **Good**: "Show me all high and critical severity findings from the latest test"
❌ **Too Technical**: "adversys_findings operation=list severity=critical"

### 4. Ask for Workflows
✅ **Good**: "I want to test 192.168.1.0/24. Set everything up and start the test."
❌ **Too Step-by-Step**: "Create target. Create test. Start test." (though this also works)

## Advanced: Explicit Tool Calls

If you need to be very specific about parameters, you can reference the tool documentation:

**You say:**
```
"Create a penetration test with these Rules of Engagement: 
destructive operations disabled, no time windows, 
and only allow reconnaissance techniques"
```

The agent will construct the appropriate JSON for the `roe` parameter.

## Troubleshooting

### Agent Doesn't Use the Tool

If the agent doesn't recognize your request:
1. **Be more explicit**: "Use the adversys_targets tool to create a target..."
2. **Check tool availability**: The tools are automatically available if they're in `python/tools/`
3. **Review system prompt**: The agent should have tool documentation in its system prompt

### Wrong Parameters

If the agent uses the tool but with wrong parameters:
1. **Be more specific**: Include all required parameters in your request
2. **Provide examples**: "Create a target like the one we made earlier"
3. **Correct the agent**: "That's not right, use target_id abc-123 instead"

### Tool Errors

If you get API errors:
1. **Check authentication**: Verify `ADVERSYS_API_URL`, `ADVERSYS_API_USERNAME`, and `ADVERSYS_API_PASSWORD` are set
2. **Verify IDs**: Make sure target_id, test_id, etc. are valid UUIDs
3. **Check API status**: Ensure the Adversys API service is running

## Example Conversation

```
You: "I want to test our web server at 192.168.1.100"

Delta: "I'll help you set up a penetration test for that server. 
Let me create a target first..."

[Agent uses adversys_targets with operation=create]

Delta: "Target created successfully. Now I'll create a penetration test..."

[Agent uses adversys_pentests with operation=create]

Delta: "Penetration test created. Should I start it now?"

You: "Yes, start it"

[Agent uses adversys_pentests with operation=start]

Delta: "Test started. I'll monitor its progress. Would you like me 
to check the status periodically?"

You: "Yes, and show me findings when they come in"

[Agent periodically uses adversys_pentests with operation=status, 
and adversys_findings with operation=list]
```

## Summary

**Key Points:**
- ✅ Just ask in natural language - no need to know tool names
- ✅ Agent automatically discovers and uses the right tools
- ✅ Be specific about what you want to accomplish
- ✅ The agent understands workflows and can chain multiple operations
- ✅ Tool documentation is automatically available to the agent

**Remember**: Delta is designed to understand your intent and use the appropriate tools automatically. You don't need to learn the tool API - just describe what you want to do!
