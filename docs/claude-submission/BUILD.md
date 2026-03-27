# Building ComplianceCow MCP Servers

This guide explains how to build, validate, and package all five ComplianceCow MCP servers for Claude submission.

## Prerequisites

### Install mcpb CLI

```bash
npm install -g @anthropic-ai/mcpb
```

Verify installation:
```bash
mcpb --version
```

### Install Python Dependencies

```bash
cd /path/to/cow-mcp
uv sync
```

## Server Overview

| Server | Environment Variable | Manifest Location |
|--------|---------------------|-------------------|
| insights | `MCP_TOOLS_TO_BE_INCLUDED=insights` | `docs/claude-submission/insights/manifest.json` |
| rules | `MCP_TOOLS_TO_BE_INCLUDED=rules` | `docs/claude-submission/rules/manifest.json` |
| workflow | `MCP_TOOLS_TO_BE_INCLUDED=workflow` | `docs/claude-submission/workflow/manifest.json` |
| metrics | `MCP_TOOLS_TO_BE_INCLUDED=metrics` | `docs/claude-submission/metrics/manifest.json` |
| issuecommands | `MCP_TOOLS_TO_BE_INCLUDED=issuecommands` | `docs/claude-submission/issuecommands/manifest.json` |

## Build Process

### Step 1: Validate Manifests

Validate all five manifests before building:

```bash
# Validate each server manifest
mcpb validate docs/claude-submission/insights/manifest.json
mcpb validate docs/claude-submission/rules/manifest.json
mcpb validate docs/claude-submission/workflow/manifest.json
mcpb validate docs/claude-submission/metrics/manifest.json
mcpb validate docs/claude-submission/issuecommands/manifest.json
```

Or validate all at once:

```bash
for server in insights rules workflow metrics issuecommands; do
  echo "Validating $server..."
  mcpb validate docs/claude-submission/$server/manifest.json
done
```

### Step 2: Prepare Server Directories

Each server needs its own directory structure for packaging. Create build directories:

```bash
mkdir -p build/{insights,rules,workflow,metrics,issuecommands}
```

### Step 3: Copy Files for Each Server

Copy the shared codebase and server-specific manifest to each build directory:

```bash
# Function to prepare a server
prepare_server() {
  local server=$1
  local build_dir="build/$server"

  echo "Preparing $server..."

  # Copy core files
  cp -r main.py "$build_dir/"
  cp -r mcpconfig/ "$build_dir/"
  cp -r mcptypes/ "$build_dir/"
  cp -r tools/ "$build_dir/"
  cp -r utils/ "$build_dir/"
  cp -r constants/ "$build_dir/"
  cp -r prompts/ "$build_dir/"
  cp -r resources/ "$build_dir/"
  cp pyproject.toml "$build_dir/"
  cp .python-version "$build_dir/" 2>/dev/null || true

  # Copy server-specific files
  cp "docs/claude-submission/$server/manifest.json" "$build_dir/"
  cp "docs/claude-submission/$server/README.md" "$build_dir/"

  # Copy icon if exists
  cp "docs/claude-submission/$server/icon.png" "$build_dir/" 2>/dev/null || \
    cp "assets/icon.png" "$build_dir/" 2>/dev/null || \
    echo "Warning: No icon.png found for $server"

  # Copy .mcpbignore
  cp .mcpbignore "$build_dir/"

  echo "$server prepared in $build_dir"
}

# Prepare all servers
for server in insights rules workflow metrics issuecommands; do
  prepare_server $server
done
```

### Step 4: Pack Each Server

Create `.mcpb` bundle files:

```bash
# Pack all servers
for server in insights rules workflow metrics issuecommands; do
  echo "Packing $server..."
  mcpb pack "build/$server" "dist/compliancecow-$server.mcpb"
done
```

### Step 5: Sign for Distribution (Optional)

For production distribution, sign the bundles:

```bash
# Self-signed (for testing)
for server in insights rules workflow metrics issuecommands; do
  mcpb sign "dist/compliancecow-$server.mcpb" --self-signed
done

# Production signing (with certificate)
for server in insights rules workflow metrics issuecommands; do
  mcpb sign "dist/compliancecow-$server.mcpb" \
    --cert path/to/cert.pem \
    --key path/to/key.pem
done
```

### Step 6: Verify Bundles

Verify the packed bundles:

```bash
for server in insights rules workflow metrics issuecommands; do
  echo "Verifying $server..."
  mcpb info "dist/compliancecow-$server.mcpb"
done
```

## Quick Build Script

Create a single build script `scripts/build-all.sh`:

```bash
#!/bin/bash
set -e

SERVERS="insights rules workflow metrics issuecommands"
BUILD_DIR="build"
DIST_DIR="dist"

# Clean previous builds
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

for server in $SERVERS; do
  echo "=========================================="
  echo "Building $server"
  echo "=========================================="

  # Create server build directory
  mkdir -p "$BUILD_DIR/$server"

  # Copy core files
  cp -r main.py "$BUILD_DIR/$server/"
  cp -r mcpconfig/ "$BUILD_DIR/$server/"
  cp -r mcptypes/ "$BUILD_DIR/$server/"
  cp -r tools/ "$BUILD_DIR/$server/"
  cp -r utils/ "$BUILD_DIR/$server/"
  cp -r constants/ "$BUILD_DIR/$server/"
  cp -r prompts/ "$BUILD_DIR/$server/"
  cp -r resources/ "$BUILD_DIR/$server/"
  cp pyproject.toml "$BUILD_DIR/$server/"
  cp .python-version "$BUILD_DIR/$server/" 2>/dev/null || true
  cp .mcpbignore "$BUILD_DIR/$server/"

  # Copy server-specific manifest and docs
  cp "docs/claude-submission/$server/manifest.json" "$BUILD_DIR/$server/"
  cp "docs/claude-submission/$server/README.md" "$BUILD_DIR/$server/"

  # Copy icon (if available)
  if [ -f "docs/claude-submission/$server/icon.png" ]; then
    cp "docs/claude-submission/$server/icon.png" "$BUILD_DIR/$server/"
  elif [ -f "assets/icon.png" ]; then
    cp "assets/icon.png" "$BUILD_DIR/$server/icon.png"
  else
    echo "Warning: No icon.png for $server"
  fi

  # Validate manifest
  echo "Validating manifest..."
  mcpb validate "$BUILD_DIR/$server/manifest.json"

  # Pack
  echo "Packing..."
  mcpb pack "$BUILD_DIR/$server" "$DIST_DIR/compliancecow-$server.mcpb"

  # Display info
  mcpb info "$DIST_DIR/compliancecow-$server.mcpb"

  echo "✓ $server built successfully"
  echo ""
done

echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo "Output files:"
ls -la "$DIST_DIR"/*.mcpb
```

Make it executable:

```bash
chmod +x scripts/build-all.sh
```

Run the build:

```bash
./scripts/build-all.sh
```

## Testing Locally

### Test with Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "compliancecow-insights": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/cow-mcp", "main.py"],
      "env": {
        "MCP_TOOLS_TO_BE_INCLUDED": "insights",
        "CCOW_HOST": "https://your-tenant.compliancecow.com/api",
        "CCOW_CLIENT_ID": "your-client-id",
        "CCOW_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Test Each Server

```bash
# Test insights server
MCP_TOOLS_TO_BE_INCLUDED=insights uv run main.py

# Test rules server
MCP_TOOLS_TO_BE_INCLUDED=rules uv run main.py

# Test workflow server
MCP_TOOLS_TO_BE_INCLUDED=workflow uv run main.py

# Test metrics server
MCP_TOOLS_TO_BE_INCLUDED=metrics uv run main.py

# Test issuecommands server
MCP_TOOLS_TO_BE_INCLUDED=issuecommands uv run main.py
```

## Submission

After building all servers:

1. Verify all `.mcpb` files are in `dist/` directory
2. Test each server with Claude Desktop
3. Prepare test credentials for the review team
4. Submit via: https://forms.gle/tyiAZvch1kDADKoP9

### Submission Checklist

- [ ] `compliancecow-insights.mcpb` built and tested
- [ ] `compliancecow-rules.mcpb` built and tested
- [ ] `compliancecow-workflow.mcpb` built and tested
- [ ] `compliancecow-metrics.mcpb` built and tested
- [ ] `compliancecow-issuecommands.mcpb` built and tested
- [ ] Test credentials prepared
- [ ] Privacy policy URL accessible
- [ ] Icon files included

## Troubleshooting

### Validation Fails

```bash
# Check for JSON syntax errors
python -m json.tool docs/claude-submission/insights/manifest.json

# Validate schema
mcpb validate docs/claude-submission/insights/manifest.json --verbose
```

### Pack Fails

```bash
# Check .mcpbignore patterns
cat .mcpbignore

# Try packing with verbose output
mcpb pack build/insights dist/test.mcpb --verbose
```

### Missing Dependencies

```bash
# Reinstall dependencies
uv sync --refresh

# Verify Python version
python --version
```

## File Structure After Build

```
cow-mcp/
├── build/
│   ├── insights/
│   │   ├── main.py
│   │   ├── manifest.json
│   │   ├── README.md
│   │   ├── icon.png
│   │   └── ... (all server files)
│   ├── rules/
│   ├── workflow/
│   ├── metrics/
│   └── issuecommands/
├── dist/
│   ├── compliancecow-insights.mcpb
│   ├── compliancecow-rules.mcpb
│   ├── compliancecow-workflow.mcpb
│   ├── compliancecow-metrics.mcpb
│   └── compliancecow-issuecommands.mcpb
└── docs/
    └── claude-submission/
        └── ... (source manifests and docs)
```
