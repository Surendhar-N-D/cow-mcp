from mcpconfig.config import mcp
from utils import utils


@mcp.tool(annotations=utils.tool_annotations("Help",read_only=True))
def help(category: str = "all") -> str:
    """
    Important: This tool should execute when user asks for help or guidance on using ComplianceCow functions.
    ComplianceCow Help Tool - Provides guidance on how to use ComplianceCow functions.
    
    Args:
        category: Help category to display. Options:
            - "all": Show all available help
            - "assessments": Assessment-related functions
            - "controls": Control-related functions
            - "evidence": Evidence-related functions
            - "dashboard": Dashboard and reporting functions
            - "assets": Asset management functions
            - "actions": Action execution functions
            - "queries": Database query functions
    
    Returns:
        Formatted help text for the specified category
    """
    
    help_content = {
        "assessments": """
📋 ASSESSMENT FUNCTIONS
====================

🔍 Discovery & Listing:
• list_all_assessment_categories() - Get all assessment categories
• list_assessments(categoryId="", categoryName="") - Get assessments by category
• fetch_recent_assessment_runs(id) - Get recent runs for an assessment
• fetch_assessment_runs(id, page=1, pageSize=0) - Get all runs with pagination

📊 Assessment Details:
• fetch_assessment_run_details(id) - Get detailed run information
• fetch_assessment_run_leaf_controls(id) - Get leaf controls for a run
• fetch_assets_summary(id) - Get asset summary for assessment

💡 Usage Examples:
- Find SOX assessments: list_assessments(categoryName="SOX")
- Get latest run: fetch_recent_assessment_runs("assessment_id")
- Paginate through runs: fetch_assessment_runs("id", page=2, pageSize=10)
        """,
        
        "controls": """
🎛️ CONTROL FUNCTIONS
==================

🔍 Finding Controls:
• fetch_controls(control_name="") - Find controls by name
• fetch_run_controls(name) - Get controls matching name from runs
• fetch_run_control_meta_data(id) - Get control metadata (assessment info)
• fetch_automated_controls_of_an_assessment(assessment_id) - Get automated controls

📋 Control Details:
• fetch_assessment_run_leaf_control_evidence(id) - Get evidence for control
• fetch_available_control_actions(assessmentName, controlNumber="", controlAlias="") - Get available actions

💡 Usage Examples:
- Search for access controls: fetch_controls(control_name="access control")
- Get control metadata: fetch_run_control_meta_data("control_id")
- Find automated controls: fetch_automated_controls_of_an_assessment("assessment_id")
        """,
        
        "evidence": """
📁 EVIDENCE FUNCTIONS
===================

🔍 Evidence Management:
• fetch_evidence_records(id) - Get evidence records by ID
• fetch_assessment_run_leaf_control_evidence(id) - Get evidence for control
• fetch_evidence_available_actions(assessment_name, control_number, control_alias, evidence_name) - Get available actions

💡 Usage Examples:
- Get evidence details: fetch_evidence_records("evidence_id")
- Check evidence actions: fetch_evidence_available_actions("SOX", "AC-1", "access_control", "evidence_name")
        """,
        
        "dashboard": """
📊 DASHBOARD & REPORTING FUNCTIONS
================================

📈 Dashboard Overview:
• get_dashboard_data(period="Q1 2024") - Get CCF dashboard summary
• get_dashboard_common_controls_details(period, complianceStatus="", controlStatus="", priority="", controlCategoryName="", page=1, pageSize=50) - Get detailed control data

🎯 Framework-Specific:
• fetch_dashboard_framework_controls(period, framework_name) - Get controls for specific framework
• fetch_dashboard_framework_summary(period, framework_name) - Get framework summary

⚠️ Risk Analysis:
• get_top_over_due_controls_detail(period="Q1 2024", count=10) - Get overdue controls
• get_top_non_compliant_controls_detail(period, count="1", page="1") - Get non-compliant controls

💡 Usage Examples:
- Q2 dashboard: get_dashboard_data(period="Q2 2024")
- SOX overdue controls: get_top_over_due_controls_detail(period="Q1 2024", count=5)
- Filter by status: get_dashboard_common_controls_details(period="Q1 2024", controlStatus="Overdue")
        """,
        
        "assets": """
🏢 ASSET MANAGEMENT FUNCTIONS
===========================

🔍 Asset Discovery:
• list_assets() - Get all assets
• fetch_assets_summary(id) - Get asset summary for assessment
• fetch_resource_types(id, page=1, pageSize=0) - Get resource types for asset run

📊 Resource Analysis:
• fetch_resources(id, resourceType, complianceStatus="", page=1, pageSize=0) - Get resources
• fetch_resources_summary(id, resourceType) - Get resource summary
• fetch_checks(id, resourceType, complianceStatus="", page=1, pageSize=0) - Get checks
• fetch_checks_summary(id, resourceType) - Get checks summary

🔧 Check Details:
• fetch_resources_with_this_check(id, resourceType, check, page=1, pageSize=0) - Get resources for specific check
• fetch_resources_with_this_check_summary(id, resourceType, check) - Get check summary

💡 Usage Examples:
- Get all assets: list_assets()
- Check EC2 compliance: fetch_resources_summary("run_id", "EC2")
- Find failed checks: fetch_checks("run_id", "S3", complianceStatus="NON_COMPLIANT")
        """,
        
        "actions": """
⚡ ACTION EXECUTION FUNCTIONS
===========================

🔍 Available Actions:
• fetch_assessment_available_actions(name="") - Get assessment-level actions
• fetch_available_control_actions(assessmentName, controlNumber="", controlAlias="", evidenceName="") - Get control actions
• fetch_evidence_available_actions(assessment_name, control_number, control_alias, evidence_name) - Get evidence actions

🚀 Execute Actions:
• execute_action(assessmentId, assessmentRunId, actionBindingId, assessmentRunControlId="", assessmentRunControlEvidenceId="", evidenceRecordIds=[]) - Execute action

⚠️ IMPORTANT: Always get user confirmation before executing actions!

💡 Usage Examples:
- Check assessment actions: fetch_assessment_available_actions(name="SOX Assessment")
- Execute control action: execute_action("assess_id", "run_id", "action_id", assessmentRunControlId="control_id")
        """,
        
        "queries": """
🔍 DATABASE QUERY FUNCTIONS
=========================

🔧 Query Tools:
• fetch_unique_node_data_and_schema(question) - Get schema and data for questions
• execute_cypher_query(query) - Execute custom Cypher queries

💡 Usage Examples:
- Explore schema: fetch_unique_node_data_and_schema("What controls are available?")
- Custom query: execute_cypher_query("MATCH (c:Control) RETURN c.name LIMIT 10")

⚠️ Advanced: These functions require knowledge of graph database queries
        """,
        
        "common_patterns": """
🔄 COMMON USAGE PATTERNS
======================

1️⃣ Assessment Workflow:
   • list_assessments() → find your assessment
   • fetch_recent_assessment_runs(id) → get latest run
   • fetch_assessment_run_details(id) → get run details

2️⃣ Control Investigation:
   • fetch_controls(control_name="keyword") → find controls
   • fetch_run_control_meta_data(id) → get assessment context
   • fetch_assessment_run_leaf_control_evidence(id) → get evidence

3️⃣ Dashboard Analysis:
   • get_dashboard_data(period="Q1 2024") → overview
   • get_top_over_due_controls_detail() → identify issues
   • get_dashboard_common_controls_details() → detailed analysis

4️⃣ Asset Compliance:
   • list_assets() → find assets
   • fetch_assets_summary(id) → get overview
   • fetch_resource_types(id) → see resource types
   • fetch_resources_summary(id, resourceType) → check compliance

5️⃣ Taking Actions:
   • fetch_available_control_actions() → see options
   • Get user confirmation
   • execute_action() → perform action
        """,
        
        "tips": """
💡 TIPS & BEST PRACTICES
======================

🔧 Pagination Tips:
• Use page and pageSize parameters for large datasets
• Start with small pageSize (5-10) if timeouts occur
• Check totalPages in response to know how many pages exist

📊 Performance Tips:
• Use summary functions (*_summary) for large datasets
• Use filters (complianceStatus, controlStatus) to narrow results
• Paginate when dealing with >50 items

🎯 Search Tips:
• Use partial names in fetch_controls() for broader results
• Try fetch_run_controls() if fetch_controls() returns no results
• Use execute_cypher_query() for complex searches

⚠️ Action Safety:
• ALWAYS fetch available actions first
• Confirm with user before executing any action
• Actions can modify system state - be careful!

📅 Period Formats:
• Use format: "Q1 2024", "Q2 2024", etc.
• Dashboard functions require proper period format
        """
    }
    
    if category.lower() == "all":
        result = "🐄 COMPLIANCECOW HELP GUIDE\n" + "="*50 + "\n\n"
        result += "Available categories: assessments, controls, evidence, dashboard, assets, actions, queries\n"
        result += "Use: compliance_cow_help(category='category_name') for specific help\n\n"
        
        for cat, content in help_content.items():
            result += content + "\n\n"
        
        return result
    
    elif category.lower() in help_content:
        return f"🐄 COMPLIANCECOW HELP - {category.upper()}\n{'='*50}\n\n{help_content[category.lower()]}"
    
    else:
        available_categories = ", ".join(help_content.keys())
        return f"❌ Unknown category: {category}\n\nAvailable categories: {available_categories}\n\nUse compliance_cow_help() to see all help."
    

    
