# ComplianceCow MCP Manifest Authoring Guide

This guide explains how to author and maintain manifest.json files for ComplianceCow MCP servers.

## Manifest Structure

```json
{
  "manifest_version": "0.3",
  "name": "compliancecow-{server}",
  "display_name": "ComplianceCow {Server Name}",
  "version": "1.0.0",
  "description": "Short description",
  "author": {...},
  "server": {...},
  "icon": "icon.png",
  "repository": {...},
  "homepage": "https://compliancecow.com",
  "documentation": "https://docs.compliancecow.com/mcp/{server}",
  "keywords": [...],
  "license": "MIT",
  "long_description": "...",
  "privacy_policies": [...],
  "tools": [...],
  "user_config": {...}
}
```

## Required Fields

### manifest_version
```json
"manifest_version": "0.3"
```
Must be "0.3" or higher for Claude submission.

### name
```json
"name": "compliancecow-insights"
```
Unique identifier. Use lowercase with hyphens.

### display_name
```json
"display_name": "ComplianceCow Insights"
```
Human-readable name shown in Claude UI.

### version
```json
"version": "1.0.0"
```
Semantic versioning (MAJOR.MINOR.PATCH).

### description
```json
"description": "Real-time compliance dashboards and asset visibility"
```
Short description (under 100 characters).

### author
```json
"author": {
  "name": "ComplianceCow",
  "email": "support@compliancecow.com",
  "url": "https://compliancecow.com"
}
```

### server
```json
"server": {
  "type": "python",
  "entry_point": "main.py",
  "mcp_config": {
    "command": "uv",
    "args": ["run", "--directory", "${__dirname}", "main.py"],
    "env": {
      "MCP_TOOLS_TO_BE_INCLUDED": "insights",
      "CCOW_HOST": "${user_config.ccow_host}",
      "CCOW_CLIENT_ID": "${user_config.ccow_client_id}",
      "CCOW_CLIENT_SECRET": "${user_config.ccow_client_secret}"
    }
  }
}
```

Key points:
- `type`: "python" for uv-based servers
- `entry_point`: Main script file
- `mcp_config.command`: "uv" for Python projects
- `mcp_config.args`: Arguments including directory
- `mcp_config.env`: Environment variable mapping

### privacy_policies
```json
"privacy_policies": [
  "https://compliancecow.com/privacy"
]
```
Array of HTTPS URLs. Required for submission.

### tools
```json
"tools": [
  {
    "name": "get_dashboard_data",
    "description": "Get dashboard summary for a compliance period"
  }
]
```
List all tools with clear descriptions.

### user_config
```json
"user_config": {
  "ccow_host": {
    "type": "string",
    "title": "ComplianceCow Host",
    "description": "Your ComplianceCow API host URL",
    "required": true,
    "sensitive": false
  },
  "ccow_client_secret": {
    "type": "string",
    "title": "Client Secret",
    "description": "OAuth Client Secret",
    "required": true,
    "sensitive": true
  }
}
```

Fields:
- `type`: "string" for text fields
- `title`: Display label
- `description`: Help text
- `required`: true/false
- `sensitive`: true for secrets (masked in UI)

## Optional Fields

### keywords
```json
"keywords": ["compliance", "dashboard", "controls", "frameworks"]
```
Search keywords for discovery.

### long_description
```json
"long_description": "Detailed description with markdown support..."
```
Extended description shown in extension details.

### screenshots
```json
"screenshots": ["screenshot1.png", "screenshot2.png"]
```
UI screenshots for the extension page.

### homepage
```json
"homepage": "https://compliancecow.com"
```
Product homepage URL.

### documentation
```json
"documentation": "https://docs.compliancecow.com/mcp/insights"
```
Documentation URL.

### license
```json
"license": "MIT"
```
SPDX license identifier.

## Server Selection

Each ComplianceCow server uses the same codebase but exposes different tools:

| Server | MCP_TOOLS_TO_BE_INCLUDED | Tool Modules |
|--------|--------------------------|--------------|
| insights | insights | dashboard, graphdb, assets, config |
| rules | rules | rules |
| workflow | workflow | workflow |
| metrics | metrics | metrics |
| issuecommands | issuecommands | forms, assistant, general |

## Variable Interpolation

Use these patterns in manifest:

| Pattern | Description |
|---------|-------------|
| `${__dirname}` | Directory containing manifest |
| `${user_config.field}` | User-provided config value |

## Validation

Before submission, validate your manifest:

1. JSON syntax is valid
2. All required fields present
3. Tool names match actual implementations
4. URLs are accessible HTTPS
5. Sensitive fields marked correctly

## Example: Adding a New Tool

When adding a tool to the server:

1. Implement the tool in the appropriate module
2. Add tool annotation:
   ```python
   @mcp.tool(annotations=utils.tool_annotations("Tool Title", read_only=True))
   ```
3. Add to manifest.json tools array:
   ```json
   {
     "name": "new_tool_name",
     "description": "What the tool does"
   }
   ```
4. Update README with usage example

## Versioning

Update version when:
- **MAJOR**: Breaking changes to tool signatures
- **MINOR**: New tools added
- **PATCH**: Bug fixes, documentation updates

## Testing

Test manifest configuration:

1. Copy manifest to local Claude config
2. Configure environment variables
3. Restart Claude Desktop
4. Verify tools appear and function

## Common Issues

### Tool Not Found
- Verify tool name matches Python function name
- Check MCP_TOOLS_TO_BE_INCLUDED is correct

### Authentication Fails
- Ensure user_config fields match env mapping
- Verify sensitive: true for secrets

### Server Won't Start
- Check uv is installed
- Verify entry_point path is correct
- Check Python dependencies installed
