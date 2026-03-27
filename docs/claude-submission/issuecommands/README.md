# ComplianceCow Issue Commands MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Assessment creation, control configuration, and evidence management for ComplianceCow.

## Features

- **Assessment Creation**: Create assessments from YAML definitions
- **Control Configuration**: Configure controls with evidence mapping
- **SQL Evidence**: Create SQL query-based evidence for automated data collection
- **Citation Management**: Attach citations to control configurations
- **Control Notes**: Document controls with notes and comments
- **Entity Hierarchy**: Navigate organizational structure

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
    "compliancecow-issuecommands": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/cow-mcp", "main.py"],
      "env": {
        "MCP_TOOLS_TO_BE_INCLUDED": "issuecommands",
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

### Example 1: Create an Assessment from YAML

**User prompt:**
```
Create a new SOC 2 assessment for Q2 2024
```

**Expected behavior:**
Server calls `create_assessment` with YAML definition:

**Sample response:**
```
Assessment Created Successfully:
- Name: SOC 2 Type II - Q2 2024
- Category: SOC 2
- Status: Active
- Controls: 89 mapped

Next Steps:
1. Configure control evidence sources
2. Map automation rules
3. Schedule assessment run
```

### Example 2: Configure Control Evidence with SQL

**User prompt:**
```
Set up SQL evidence for the user access control to pull data from our identity system
```

**Expected behavior:**
1. Server calls `list_assessments` to find the assessment
2. Calls `list_assessment_control_configs` to find the control
3. Calls `get_context_tables` to show available data sources
4. Calls `validate_sql_query` to check the query
5. Calls `create_sql_query_evidence` to create the evidence

**Sample response:**
```
SQL Evidence Configuration:
- Control: User Access Management (CC-AC-001)
- Evidence Name: Active Directory Users

Available Tables:
- identity.users
- identity.group_memberships
- identity.access_logs

SQL Query:
SELECT user_id, display_name, groups, last_login
FROM identity.users
WHERE status = 'active'

Query validated successfully!
Evidence configuration created.
```

### Example 3: Add Citation to Control

**User prompt:**
```
Add a citation reference for the encryption control pointing to our security policy
```

**Expected behavior:**
1. Server calls `suggest_control_config_citations` for suggestions
2. Calls `attach_citation_to_control_config` to add the citation

**Sample response:**
```
Citation Suggestions for Encryption Control:
1. Information Security Policy - Section 5.2 (Recommended)
2. Data Classification Standard - Section 3.1
3. Encryption Guidelines v2.0

Adding: Information Security Policy - Section 5.2
- Reference: ISP-5.2-ENC
- Type: Policy Document
- Status: Active

Citation attached successfully!
```

### Example 4: Get Evidence Sample Data

**User prompt:**
```
Show me sample evidence data for the access review control
```

**Expected behavior:**
1. Server calls `list_assessment_control_configs` to find the control
2. Calls `get_evidence_sample_data` to retrieve samples

**Sample response:**
```
Evidence Sample Data for Access Review Control:

Evidence: User Access Records
Sample Records (3 of 500):

| User ID | Name | Last Review | Status |
|---------|------|-------------|--------|
| U001 | John Smith | 2024-02-15 | Reviewed |
| U002 | Jane Doe | 2024-02-14 | Reviewed |
| U003 | Bob Wilson | 2024-01-10 | Pending |

Total Records: 500
Last Updated: 2024-03-15
```

## Available Tools

### Assessment Management
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `create_assessment` | Create assessment from YAML | No |
| `list_assessments` | List all assessments | Yes |
| `list_assessment_control_configs` | List control configs | Yes |
| `create_control_config` | Create control config | No |
| `update_control_config_contexts` | Update contexts | No |
| `mark_control_ready_for_execution` | Mark ready | No |

### Evidence Configuration
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `create_sql_query_evidence` | Create SQL evidence | No |
| `list_sql_query_evidence` | List SQL evidence | Yes |
| `update_sql_query_evidence` | Update SQL evidence | No |
| `validate_sql_query` | Validate SQL | Yes |
| `fetch_sql_query_feedback` | Get SQL feedback | Yes |
| `get_evidence_sample_data` | Get sample data | Yes |
| `fetch_control_source_summary` | Get source summary | Yes |
| `get_context_tables` | Get context tables | Yes |

### Citations & Notes
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `suggest_control_config_citations` | Get suggestions | Yes |
| `attach_citation_to_control_config` | Attach citation | No |
| `create_control_config_note` | Create note | No |
| `list_control_config_notes` | List notes | Yes |
| `update_control_config_note` | Update note | No |

### Utilities
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `get_entity_hierarchy` | Get hierarchy | Yes |
| `fetch_rule_readme` | Get rule docs | Yes |
| `create_downloadable_file` | Create file | No |

## Privacy Policy

ComplianceCow Issue Commands connects to your ComplianceCow tenant to manage assessments and control configurations. All data remains within your tenant and is transmitted securely via HTTPS.

- **Data Collection**: No data is collected by this MCP server. All operations execute against your ComplianceCow instance.
- **Authentication**: OAuth credentials are used solely for API authentication and are not stored or transmitted elsewhere.
- **Data Storage**: This server does not persist any data locally.

For complete privacy information, see: https://compliancecow.com/privacy

## Troubleshooting

### SQL Query Validation Errors

If SQL validation fails:
1. Check table and column names
2. Verify SQL syntax
3. Ensure you have access to the referenced tables

### Assessment Creation Fails

If assessment creation fails:
1. Validate YAML syntax
2. Check that referenced frameworks exist
3. Ensure category name is valid

### Evidence Sample Returns Empty

If no evidence samples are returned:
1. Verify the control has evidence configured
2. Check that assessment has been executed
3. Ensure evidence collection completed successfully

## Support

- **Documentation**: https://docs.compliancecow.com
- **Issues**: https://github.com/compliancecow/cow-mcp/issues
- **Email**: support@compliancecow.com
