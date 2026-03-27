# ComplianceCow Metrics MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Metrics assessment, tracking, and evidence management for ComplianceCow.

## Features

- **Metrics Assessment**: Create and manage compliance metrics assessments
- **Evidence Collection**: Retrieve sample evidence data for metrics analysis
- **SQL Query Evidence**: Create SQL-based evidence queries for automated data collection
- **CEL Expressions**: Use Common Expression Language for metric calculations
- **Citation Management**: Suggest and attach citations to metrics
- **Metrics Linking**: Link source metrics to target metrics for aggregation

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
    "compliancecow-metrics": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/cow-mcp", "main.py"],
      "env": {
        "MCP_TOOLS_TO_BE_INCLUDED": "metrics",
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
| `METRICS_ASSESSMENT_NAME` | No | Metrics assessment name (default: "Metric Manager") |
| `METRICS_CATEGORY_NAME` | No | Metrics category name (default: "Metric Manager") |

## Usage Examples

### Example 1: Get Metrics Overview

**User prompt:**
```
Show me all metrics and their current values
```

**Expected behavior:**
1. Server calls `get_metrics_assessment` to get the metrics assessment
2. Calls `get_all_assessment_metrics` to retrieve all metrics
3. Returns a summary of metrics with their values

**Sample response:**
```
Metrics Assessment: Metric Manager

Metrics Summary:
1. User Access Review Completion Rate
   - Category: Access Control
   - Value: 94.5%
   - Status: On Target

2. Vulnerability Remediation Time
   - Category: Security Operations
   - Value: 3.2 days (avg)
   - Status: Needs Improvement

3. Incident Response Time
   - Category: Security Operations
   - Value: 2.1 hours
   - Status: On Target
```

### Example 2: Get Evidence Sample Data

**User prompt:**
```
Show me sample data for the encryption compliance metric
```

**Expected behavior:**
1. Server calls `list_assets` to find relevant assets
2. Calls `get_assets_data` to get metrics with evidence
3. Calls `get_asset_metrics_evidence_sample_data` for the selected metric

**Sample response:**
```
Metric: Encryption at Rest Compliance

Evidence: S3 Bucket Encryption Status
Sample Records (3 of 150):

| Bucket Name | Encryption | Status |
|------------|------------|--------|
| prod-data | AES-256 | Compliant |
| logs-backup | SSE-KMS | Compliant |
| temp-uploads | None | Non-Compliant |

Summary: 145/150 buckets encrypted (96.7%)
```

### Example 3: Create SQL Query Evidence

**User prompt:**
```
Create an SQL query to track the number of active users with MFA enabled
```

**Expected behavior:**
1. Server calls `validate_sql_query_and_cel` to validate the query
2. Calls `create_sql_query_evidence` to create the evidence

**Sample response:**
```
SQL Query Evidence Created:
- Name: MFA Enabled Users Count
- Query: SELECT COUNT(*) FROM users WHERE mfa_enabled = true AND status = 'active'
- Status: Valid

Next Steps:
- Run the metrics assessment to collect data
- View results in the metrics dashboard
```

### Example 4: Add CEL Expression for Calculation

**User prompt:**
```
Calculate the MFA adoption rate as a percentage
```

**Expected behavior:**
Server calls `add_cel_expression_to_metrics` with the calculation:

**Sample response:**
```
CEL Expression Added:
- Metric: MFA Adoption Rate
- Expression: (mfa_enabled_users / total_active_users) * 100
- Result Type: Percentage

The metric will be calculated automatically during assessment runs.
```

## Available Tools

### Assessment Management
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `get_metrics_assessment` | Get or create metrics assessment | Yes |
| `run_metrics_assessment` | Trigger assessment run | No |
| `get_all_recent_assessment_run_details` | Get recent runs | Yes |
| `get_all_metrics_of_run` | Get metrics from run | Yes |

### Metrics Management
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `add_metric` | Add new metric | No |
| `update_metric` | Update metric | No |
| `get_all_metrics_categories` | Get categories | Yes |
| `get_all_assessment_metrics` | Get all metrics | Yes |

### Evidence & Data
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `list_assets` | List assets | Yes |
| `get_assets_data` | Get asset data | Yes |
| `get_asset_metrics_evidence_sample_data` | Get evidence samples | Yes |
| `get_metrics_evidence_sample_data` | Get metrics evidence | Yes |
| `fetch_metrics_source_summary` | Get source summary | Yes |

### SQL & CEL
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `validate_sql_query_and_cel` | Validate queries | Yes |
| `create_sql_query_evidence` | Create SQL evidence | No |
| `list_sql_query_evidence` | List SQL evidence | Yes |
| `update_sql_query_evidence` | Update SQL evidence | No |
| `add_cel_expression_to_metrics` | Add CEL expression | No |
| `update_cel_expression_to_metrics` | Update CEL expression | No |
| `get_cel_expression_for_metrics` | Get CEL expression | Yes |

### Citations & Notes
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `suggest_metrics_citations` | Get citation suggestions | Yes |
| `attach_citation_to_metrics` | Attach citation | No |
| `create_metrics_note` | Create note | No |
| `list_metrics_notes` | List notes | Yes |
| `update_metrics_note` | Update note | No |

### Linking
| Tool | Description | Read-Only |
|------|-------------|-----------|
| `link_source_metrics_to_target_metric` | Link metrics | No |

## Privacy Policy

ComplianceCow Metrics connects to your ComplianceCow tenant to manage compliance metrics. All data remains within your tenant and is transmitted securely via HTTPS.

- **Data Collection**: No data is collected by this MCP server. All metrics operations execute against your ComplianceCow instance.
- **Authentication**: OAuth credentials are used solely for API authentication and are not stored or transmitted elsewhere.
- **Data Storage**: This server does not persist any data locally.

For complete privacy information, see: https://compliancecow.com/privacy

## Troubleshooting

### No Metrics Found

If no metrics are returned:
1. Verify the metrics assessment exists in your tenant
2. Check that metrics have been configured
3. Ensure your user has access to the metrics module

### SQL Query Validation Fails

If SQL validation fails:
1. Check SQL syntax for errors
2. Verify table and column names exist
3. Ensure the query returns compatible data types

## Support

- **Documentation**: https://docs.compliancecow.com
- **Issues**: https://github.com/compliancecow/cow-mcp/issues
- **Email**: support@compliancecow.com
