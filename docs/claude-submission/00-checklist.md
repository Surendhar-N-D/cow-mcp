# ComplianceCow MCP Server Submission Checklist

This checklist ensures all five ComplianceCow MCP servers are ready for Claude submission.

## Pre-Submission Requirements

### 1. Tool Annotations (Required - Immediate Rejection if Missing)

- [ ] All tools have `readOnlyHint: true` for read-only operations
- [ ] All tools have `destructiveHint: true` for write/modify operations
- [ ] Annotations are accurate and reflect actual tool behavior

**Verify with:**
```bash
grep -r "tool_annotations" tools/
```

### 2. Privacy Policy (Required)

- [ ] Privacy section in each server's README.md
- [ ] `privacy_policies` array in each manifest.json
- [ ] URLs are publicly accessible HTTPS

**Privacy URLs:**
- All servers: `https://compliancecow.com/privacy`

### 3. Documentation (Required)

Each server README must contain:

| Section | insights | rules | workflow | metrics | issuecommands |
|---------|----------|-------|----------|---------|---------------|
| Description | ✓ | ✓ | ✓ | ✓ | ✓ |
| Features | ✓ | ✓ | ✓ | ✓ | ✓ |
| Installation | ✓ | ✓ | ✓ | ✓ | ✓ |
| Configuration | ✓ | ✓ | ✓ | ✓ | ✓ |
| Usage Examples (min 3) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Privacy Policy | ✓ | ✓ | ✓ | ✓ | ✓ |
| Support Contact | ✓ | ✓ | ✓ | ✓ | ✓ |

### 4. Usage Examples (Required - Minimum 3 per server)

Each server has 4 working examples demonstrating:

| Server | Example 1 | Example 2 | Example 3 | Example 4 |
|--------|-----------|-----------|-----------|-----------|
| insights | Dashboard overview | Overdue controls | Asset compliance | Graph queries |
| rules | Create rule | Schedule execution | Generate docs | Check status |
| workflow | Create workflow | List events | Trigger workflow | Custom event |
| metrics | Metrics overview | Evidence sample | SQL query | CEL expression |
| issuecommands | Submit form | Create assessment | SQL evidence | Add citation |

### 5. Manifest Requirements (Required)

Each manifest.json must include:

| Field | Required | Notes |
|-------|----------|-------|
| `manifest_version` | Yes | Must be "0.3" or higher |
| `name` | Yes | Unique identifier |
| `display_name` | Yes | Human-readable name |
| `version` | Yes | SemVer format |
| `description` | Yes | Short description |
| `author` | Yes | Name, email, URL |
| `server` | Yes | Entry point and config |
| `icon` | Yes | icon.png required |
| `repository` | Yes | Git URL |
| `privacy_policies` | Yes | Array of URLs |
| `tools` | Yes | Tool list with descriptions |
| `user_config` | Yes | Required credentials |

### 6. Testing Requirements (Required)

Pre-submission testing across environments:

- [ ] Development environment (with API credentials)
- [ ] Clean environment (without dev tools)
- [ ] macOS testing
- [ ] Windows testing (if applicable)
- [ ] Claude Desktop application

### 7. Test Credentials (Required)

Prepare test account details for submission:

| Server | Credentials Needed |
|--------|-------------------|
| All | CCOW_HOST, CCOW_CLIENT_ID, CCOW_CLIENT_SECRET |

## Server-Specific Checklists

### insights
- [ ] manifest.json complete
- [ ] README.md with 4 examples
- [ ] 20 tools documented
- [ ] Dashboard tools functional
- [ ] Asset tools functional
- [ ] GraphDB tools functional

### rules
- [ ] manifest.json complete
- [ ] README.md with 4 examples
- [ ] 50+ tools documented
- [ ] Rule management functional
- [ ] Asset scheduling functional
- [ ] Documentation generation functional

### workflow
- [ ] manifest.json complete
- [ ] README.md with 4 examples
- [ ] 23 tools documented
- [ ] Event management functional
- [ ] Workflow CRUD functional
- [ ] Trigger execution functional

### metrics
- [ ] manifest.json complete
- [ ] README.md with 4 examples
- [ ] 26 tools documented
- [ ] Assessment management functional
- [ ] SQL evidence functional
- [ ] CEL expressions functional

### issuecommands
- [ ] manifest.json complete
- [ ] README.md with 4 examples
- [ ] 35 tools documented
- [ ] Form management functional
- [ ] Assessment creation functional
- [ ] Control configuration functional

## Common Rejection Reasons

1. **Missing tool annotations** - Ensure all tools have safety annotations
2. **Portability failures** - Test in clean environment
3. **Missing privacy policies** - Must be in README AND manifest
4. **Insufficient examples** - Minimum 3 working examples per server
5. **Incomplete documentation** - All required sections must be present

## Submission Process

1. Complete all checklist items above
2. Run mcpb validation (if available)
3. Test in Claude Desktop
4. Submit via: https://forms.gle/tyiAZvch1kDADKoP9

## Files to Submit

For each server:
- `manifest.json`
- `README.md`
- `icon.png` (to be added)
- Source code (main.py and tools/)

## Contact

- **Support**: support@compliancecow.com
- **Issues**: https://github.com/compliancecow/cow-mcp/issues
