# ComplianceCow MCP Servers

ComplianceCow exposes five Claude-ready MCP server bundles from this repository:

- `insights`
- `rules`
- `workflow`
- `metrics`
- `issuecommands`

Each bundle runs the same `main.py` entry point and is selected through the `MCP_TOOLS_TO_BE_INCLUDED` environment variable. This keeps the packaging model simple while letting Claude Desktop install each server as a separate extension.

## Publish-Ready Documentation

The Claude submission pack is under [docs/claude-submission](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/README.md). It contains:

- A submission checklist: [00-checklist.md](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/00-checklist.md)
- A manifest authoring guide: [manifest-guide.md](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/manifest-guide.md)
- A dedicated README and manifest template for each publishable server:
  - [insights](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/insights/README.md)
  - [rules](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/rules/README.md)
  - [workflow](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/workflow/README.md)
  - [metrics](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/metrics/README.md)
  - [issuecommands](/Users/surendharnd/projects/cow-mcp/docs/claude-submission/issuecommands/README.md)

## Runtime Selection

Use one bundle per Claude extension:

```bash
MCP_TOOLS_TO_BE_INCLUDED=insights
MCP_TOOLS_TO_BE_INCLUDED=rules
MCP_TOOLS_TO_BE_INCLUDED=workflow
MCP_TOOLS_TO_BE_INCLUDED=metrics
MCP_TOOLS_TO_BE_INCLUDED=issuecommands
```

`issuecommands` maps to the forms-oriented toolset used for issue and action workflows. `metrics` is accepted as the public bundle name and resolves to the underlying metrics tool module.

## Local Development

```bash
uv run main.py
```

Required environment variables:

- `CCOW_HOST`
- `CCOW_CLIENT_ID`
- `CCOW_CLIENT_SECRET`

Optional:

- `METRICS_ASSESSMENT_NAME`
- `METRICS_CATEGORY_NAME`
- `CCOW_MCP_SERVER_PORT`

## Packaging Note

For MCPB packaging, use the root [`.mcpbignore`](/Users/surendharnd/projects/cow-mcp/.mcpbignore) so test fixtures, caches, and local build artifacts do not get bundled into the distributable package.
