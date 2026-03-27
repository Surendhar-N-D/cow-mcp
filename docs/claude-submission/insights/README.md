# ComplianceCow Insights MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Real-time compliance dashboards, asset inventory, and control framework visibility for ComplianceCow.

## Features

- **Compliance Dashboards**: Access Common Control Framework (CCF) dashboards with period-based filtering (e.g., Q1 2024)
- **Control Status Tracking**: Monitor controls across states: Completed, In Progress, Overdue, Pending
- **Framework Analytics**: View compliance percentages and control breakdowns by framework
- **Asset Inventory**: Browse cloud infrastructure assets with resource type categorization
- **Compliance Checks**: Analyze pass/fail rates for compliance checks per resource
- **Graph Database Queries**: Execute Cypher queries against the compliance knowledge graph

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

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CCOW_HOST` | Yes | ComplianceCow API host URL |
| `CCOW_CLIENT_ID` | Yes | OAuth Client ID |
| `CCOW_CLIENT_SECRET` | Yes | OAuth Client Secret |

## Usage Examples

### Example 1: Get Compliance Dashboard Overview

**User prompt:**
```
Show me the compliance dashboard for Q1 2024
```

**Expected behavior:**
The server calls `get_dashboard_data` with period "Q1 2024" and returns:
- Total controls count
- Control status breakdown (Completed, In Progress, Overdue, Pending)
- Overall compliance percentage
- Framework-level summaries

**Sample response:**
```
Dashboard Summary for Q1 2024:
- Total Controls: 245
- Compliance: 87.3%
- Status Breakdown:
  - Completed: 180
  - In Progress: 35
  - Overdue: 15
  - Pending: 15
```

### Example 2: Find Overdue Controls

**User prompt:**
```
What are the top 10 overdue controls for this quarter?
```

**Expected behavior:**
The server calls `get_top_over_due_controls_detail` and returns controls sorted by overdue severity:

**Sample response:**
```
Top Overdue Controls:
1. Access Review - Annual User Access Review
   - Assigned To: john@company.com
   - Due Date: 2024-01-15
   - Priority: High

2. Encryption - Data At Rest Encryption
   - Assigned To: security@company.com
   - Due Date: 2024-01-20
   - Priority: High
...
```

### Example 3: Explore Cloud Asset Compliance

**User prompt:**
```
Show me compliance status for EC2 instances in our AWS assessment
```

**Expected behavior:**
1. Server calls `list_assets` to find the AWS assessment
2. Calls `fetch_assets_summary` with the assessment ID
3. Calls `fetch_resource_types` to find EC2 resources
4. Calls `fetch_checks` for EC2 resource type

**Sample response:**
```
EC2 Instance Compliance:
- Total Instances: 47
- Compliant: 42 (89.4%)
- Non-Compliant: 5 (10.6%)

Failed Checks:
- EBS Encryption: 3 instances non-compliant
- IMDSv2 Required: 2 instances non-compliant
```

### Example 4: Query Compliance Graph

**User prompt:**
```
Find all controls under SOC 2 framework that have evidence attached
```

**Expected behavior:**
Server uses `execute_cypher_query` to run a graph query:

**Sample response:**
```
SOC 2 Controls with Evidence:
- CC1.1 - Control Environment: 3 evidence records
- CC2.1 - Information and Communication: 5 evidence records
- CC6.1 - Logical Access: 8 evidence records
...
```

## Available Tools

| Tool | Description | Read-Only |
|------|-------------|-----------|
| `get_dashboard_review_periods` | Fetch available review periods | Yes |
| `get_dashboard_data` | Get dashboard summary for a period | Yes |
| `fetch_dashboard_framework_controls` | Get framework control details | Yes |
| `fetch_dashboard_framework_summary` | Get framework summary | Yes |
| `get_dashboard_common_controls_details` | Get paginated control details | Yes |
| `get_top_over_due_controls_detail` | Get overdue controls | Yes |
| `get_top_non_compliant_controls_detail` | Get non-compliant controls | Yes |
| `fetch_unique_node_data_and_schema` | Get graph node data | Yes |
| `execute_cypher_query` | Execute Cypher queries | No |
| `list_assets` | List all assets | Yes |
| `fetch_assets_summary` | Get asset run summary | Yes |
| `fetch_resource_types` | Get resource types | Yes |
| `fetch_checks` | Get compliance checks | Yes |
| `fetch_resources` | Get resources | Yes |
| `fetch_resources_by_check_name` | Get resources by check | Yes |
| `fetch_checks_summary` | Get checks summary | Yes |
| `fetch_resources_summary` | Get resources summary | Yes |
| `fetch_resources_by_check_name_summary` | Get check resources summary | Yes |
| `list_all_assessment_categories` | List assessment categories | Yes |
| `list_assessments` | List assessments | Yes |

## Privacy Policy

ComplianceCow Insights connects to your ComplianceCow tenant to retrieve compliance data. All data remains within your tenant and is transmitted securely via HTTPS.

- **Data Collection**: No data is collected by this MCP server. All queries are executed against your ComplianceCow instance.
- **Authentication**: OAuth credentials are used solely for API authentication and are not stored or transmitted elsewhere.
- **Data Storage**: This server does not persist any data locally.

For complete privacy information, see: https://compliancecow.com/privacy

## Troubleshooting

### Authentication Errors

If you receive authentication errors:
1. Verify your `CCOW_HOST` URL ends with `/api`
2. Confirm your Client ID and Secret are correct
3. Ensure your API credentials have the necessary permissions

### No Data Returned

If queries return empty results:
1. Verify the review period format (e.g., "Q1 2024")
2. Check that assessments exist in your ComplianceCow tenant
3. Confirm your user has access to the requested data

## Support

- **Documentation**: https://docs.compliancecow.com
- **Issues**: https://github.com/compliancecow/cow-mcp/issues
- **Email**: support@compliancecow.com
