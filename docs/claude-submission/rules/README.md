# ComplianceCow Rules MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Compliance rule management, automation, and control mapping for ComplianceCow.

## Features

- **Rule Management**: Create, update, and publish compliance rules with input/output mapping
- **Control Mapping**: Attach rules to controls for automated compliance verification
- **Asset Checks**: Manage compliance checks and associate them with assets
- **Scheduling**: Schedule automated rule executions
- **Documentation**: Generate design notes and README files for rules
- **Execution Tracking**: Monitor rule execution progress and fetch outputs
- **Citation Management**: Suggest and add citations to control configurations

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- ComplianceCow account with API credentials

### Claude Desktop Configuration

Add to your Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "compliancecow-rules": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/cow-mcp", "main.py"],
      "env": {
        "MCP_TOOLS_TO_BE_INCLUDED": "rules",
        "CCOW_HOST": "https://your-tenant.compliancecow.com/api",
        "CCOW_CLIENT_ID": "your-client-id",
        "CCOW_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CCOW_HOST` | Yes | ComplianceCow API host URL |
| `CCOW_CLIENT_ID` | Yes | OAuth Client ID |
| `CCOW_CLIENT_SECRET` | Yes | OAuth Client Secret |

## Usage Examples

### Example 1: Create and Attach a Rule to a Control

**User prompt:**
```
Create a rule to check S3 bucket encryption and attach it to the Data Encryption control
```

**Expected behavior:**
1. Server calls `fetch_tasks_suggestions` to find relevant templates
2. Calls `create_rule` with appropriate configuration
3. Calls `fetch_leaf_controls_of_an_assessment` to find the control
4. Calls `attach_rule_to_control` to link them

**Sample response:**
```
Created rule: S3-Bucket-Encryption-Check
- Rule ID: rule-abc123
- Status: Draft

Attached to control: CC-DE-001 (Data Encryption)
- Assessment: SOC 2 Type II
- Control Status: Automated
```

### Example 2: Schedule Asset Execution

**User prompt:**
```
Schedule the AWS Security assessment to run every Monday at 9 AM
```

**Expected behavior:**
1. Server calls `list_assets` to find the AWS Security asset
2. Calls `schedule_asset_execution` with the schedule configuration

**Sample response:**
```
Asset execution scheduled:
- Asset: AWS Security Assessment
- Schedule: Every Monday at 9:00 AM UTC
- Next Run: 2024-03-18 09:00 UTC
- Schedule ID: sched-xyz789
```

### Example 3: Generate Rule Documentation

**User prompt:**
```
Generate design notes and README for the IAM-Policy-Review rule
```

**Expected behavior:**
1. Server calls `fetch_cc_rule_by_name` to get rule details
2. Calls `generate_design_notes_preview` to preview notes
3. Calls `create_design_notes` to save
4. Calls `generate_rule_readme_preview` to preview README
5. Calls `create_rule_readme` to save

**Sample response:**
```
Documentation generated for IAM-Policy-Review:

Design Notes:
- Purpose: Review IAM policies for overly permissive access
- Inputs: AWS credentials, policy list
- Outputs: Policy analysis report
- Control Mapping: AC-6 Least Privilege

README created with:
- Prerequisites
- Configuration steps
- Usage instructions
- Expected outputs
```

### Example 4: Check Rule Publishing Status

**User prompt:**
```
Check the publishing status of my encryption rules and publish any that are ready
```

**Expected behavior:**
1. Server calls `fetch_cc_rules_list` to get rules
2. Calls `check_rule_publish_status` for each rule
3. Calls `publish_rule` for rules ready to publish

**Sample response:**
```
Rule Publishing Status:
1. S3-Encryption-Check: Published ✓
2. EBS-Encryption-Check: Ready to publish
   - Publishing... Done ✓
3. RDS-Encryption-Check: Draft (needs configuration)

2 rules published, 1 rule needs additional configuration.
```

## Available Tools

### Rule Management
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `fetch_cc_rules_list` | List all compliance rules | Yes |
| `fetch_cc_rule_by_id` | Get rule by ID | Yes |
| `fetch_cc_rule_by_name` | Get rule by name | Yes |
| `create_rule` | Create new rule | No |
| `update_rule` | Update existing rule | No |
| `publish_rule` | Publish a rule | No |
| `check_rule_publish_status` | Check rule publish status | Yes |
| `execute_rule` | Execute a rule | No |

### Control & Asset Management
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `attach_rule_to_control` | Attach rule to control | No |
| `fetch_leaf_controls_of_an_assessment` | Get leaf controls | Yes |
| `verify_control_in_assessment` | Verify control exists | Yes |
| `list_assets` | List all assets | Yes |
| `list_checks` | List all checks | Yes |
| `add_check_to_asset` | Add check to asset | No |
| `create_asset_and_check` | Create asset with checks | No |

### Scheduling
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `schedule_asset_execution` | Schedule execution | No |
| `list_asset_schedules` | List schedules | Yes |
| `delete_asset_schedule` | Delete schedule | No |

### Documentation
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `generate_design_notes_preview` | Preview design notes | Yes |
| `create_design_notes` | Create design notes | No |
| `fetch_rule_design_notes` | Fetch design notes | Yes |
| `generate_rule_readme_preview` | Preview README | Yes |
| `create_rule_readme` | Create README | No |
| `update_rule_readme` | Update README | No |

### Task Execution
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `fetch_tasks_suggestions` | Get task suggestions | Yes |
| `get_tasks_summary` | Get tasks summary | Yes |
| `get_template_guidance` | Get template guidance | Yes |
| `execute_task` | Execute a task | No |
| `fetch_execution_progress` | Track execution | Yes |
| `fetch_output_file` | Get execution output | Yes |

## Privacy Policy

ComplianceCow Rules connects to your ComplianceCow tenant to manage compliance rules and configurations. All data remains within your tenant and is transmitted securely via HTTPS.

- **Data Collection**: No data is collected by this MCP server. All operations execute against your ComplianceCow instance.
- **Authentication**: OAuth credentials are used solely for API authentication and are not stored or transmitted elsewhere.
- **Data Storage**: This server does not persist any data locally.

For complete privacy information, see: https://compliancecow.com/privacy

## Troubleshooting

### Rule Publishing Fails

If rule publishing fails:
1. Verify the rule has all required configurations
2. Check that dependencies (tasks, templates) are available
3. Ensure your user has publish permissions

### Execution Errors

If task execution fails:
1. Check input parameters are correctly formatted
2. Verify required credentials/integrations are configured
3. Review execution logs via `fetch_execution_progress`

## Support

- **Documentation**: https://docs.compliancecow.com
- **Issues**: https://github.com/compliancecow/cow-mcp/issues
- **Email**: support@compliancecow.com
