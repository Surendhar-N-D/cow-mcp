import json
import traceback
import base64
import asyncio
from typing import List
from typing import Tuple
import base64


from utils import utils
from utils.debug import logger
from mcpconfig.config import mcp

from constants import constants
from mcptypes import workflow_tools_type as vo
import yaml
from fastmcp import Context

import constants.error_constants as error_constants
@mcp.tool(annotations=utils.tool_annotations("List Workflow Event Categories",read_only=True))
async def list_workflow_event_categories(ctx: Context | None = None) -> vo.WorkflowEventCategoryListVO:
    """
    Retrieve available workflow event categories.
    
    Event categories help organize workflow triggers by type (e.g., assessment events, 
    time-based events, user actions). This is useful for filtering and selecting 
    appropriate events when building workflows.
    
    Returns:
        - eventCategories: List of event categories with type and displayable name
        - error: Error message if retrieval fails
    """
    try:
        logger.info("list_workflow_event_categories: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_EVENT_CATEGORIES, "GET", ctx=ctx)
        logger.debug("workflow event categories output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_event_categories")
        if error:
            logger.error("workflow event categories error: {}\n".format(output))
            return vo.WorkflowEventCategoryListVO(error=error)
        
        eventCategories: List[vo.WorkflowEventCategoryItemVO]=[]
        for item in output["items"]:
            if "type" in item and "displayable" in item:
                eventCategories.append(vo.WorkflowEventCategoryItemVO.model_validate(item))
        
        logger.debug("modified event categories: {}\n".format(vo.WorkflowEventCategoryListVO(eventCategories=eventCategories).model_dump()))

        return vo.WorkflowEventCategoryListVO(eventCategories=eventCategories)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow event categories: {}\n".format(e))
        return vo.WorkflowEventCategoryListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_event_categories"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Events",read_only=True))
async def list_workflow_events(ctx: Context | None = None) -> vo.WorkflowEventListVO:
    """
    Retrieve available workflow events that can trigger workflows.
    
    Events are the starting points of workflows. Each event has a payload that 
    provides data to subsequent workflow nodes. Events are categorized into two types:
    
    **System Events**: Automatically triggered by the system when specific actions occur.
    Examples include:
    - Assessment run completed
    - Form submitted
    - Scheduled time-based triggers
    
    **Custom Events**: Manually triggered events that can be used to:
    - Trigger workflows from within other workflows
    - Integrate with external systems
    - Enable manual workflow execution
    
    Returns:
        - systemEvents (List[WorkflowEventVO]): A list of system events that are automatically triggered.
            - id (str)
            - categoryId (str)
            - desc (str)
            - displayable (str)
            - payload [List[WorkflowPayloadVO]]
            - status (str)
            - type (str)
        - customEvents (List[WorkflowEventVO]): A list of custom events that can be manually triggered.
            - id (str)
            - categoryId (str)
            - desc (str)
            - displayable (str)
            - payload [List[WorkflowPayloadVO]]
            - status (str)
            - type (str)
        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("Fetching workflow events")
        
        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_EVENTS, "GET", ctx=ctx)
        logger.debug(f"Events response: {output}")
        
        error = utils.build_structured_error(output, "list_workflow_events")
        if error:
            logger.error(f"Failed to fetch events: {output}")
            return vo.WorkflowEventListVO(error=error)
        
        systemEvents: List[vo.WorkflowEventVO] = []
        customEvents: List[vo.WorkflowEventVO] = []
        
        for item in output.get("items", []):
            if "type" in item and "displayable" in item and item.get("status") == "Active":
                event = vo.WorkflowEventVO.model_validate(item)
                
                # Categorize events based on eventType
                if item.get("type") == "CUSTOM_EVENT":
                    customEvents.append(event)
                else:
                    systemEvents.append(event)
        
        logger.debug("modified events - systemEvents: {}, customEvents: {}\n".format(
            len(systemEvents), len(customEvents)))

        return vo.WorkflowEventListVO(systemEvents=systemEvents, customEvents=customEvents)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow events: {}\n".format(e))
        return vo.WorkflowEventListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_events"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Activity Types",read_only=True))
async def list_workflow_activity_types(ctx: Context | None = None) -> vo.WorkflowActivityTypeListVO:
    """
    Get available workflow activity types.
    
    Activity types define what kind of actions can be performed in workflow nodes:
    - Pre-build Function: Execute predefined logic
    - Pre-build Rule: Execute a rule
    - Pre-build Task: Trigger a predefined task
    
    Returns:
        List of available activity types
    """
    try:
        return vo.WorkflowActivityTypeListVO(
            activityTypes=['Pre-build Function', 'Pre-build Rule', 'Pre-build Task', 'Existing Workflow']
        )
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("list_workflow_activity_types error: {}\n".format(e))
        return vo.WorkflowActivityTypeListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_activity_types"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Function Categories",read_only=True))
async def list_workflow_function_categories(ctx: Context | None = None) -> vo.WorkflowActivityCategoryListVO:
    """
    Retrieve available workflow function categories.
    
    Function categories help organize workflow activities by type. This is useful 
    for filtering and selecting appropriate functions when building workflows.
    
    Returns:
        - activity categories (List[WorkflowActivityCategoryItemVO]): List of activity categories.
            - name (str): Name of the category.
        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("list_workflow_activity_categories: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_ACTIVITY_CATEGORIES, "GET", ctx=ctx)
        logger.debug("workflow activity categories output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_function_categories")
        if error:
            logger.error("workflow activity categories error: {}\n".format(output))
            return vo.WorkflowActivityCategoryListVO(error=error)
        
        activityCategories: List[vo.WorkflowActivityCategoryItemVO]=[]
        for item in output["items"]:
            if "displayable" in item:
                activityCategories.append(vo.WorkflowActivityCategoryItemVO.model_validate(item))
        
        logger.debug("modified activity categories: {}\n".format(vo.WorkflowActivityCategoryListVO(activityCategories=activityCategories).model_dump()))

        return vo.WorkflowActivityCategoryListVO(activityCategories=activityCategories)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow activity categories: {}\n".format(e))
        return vo.WorkflowActivityCategoryListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_function_categories"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Functions",read_only=True))
async def list_workflow_functions(ctx: Context | None = None) -> vo.WorkflowActivityListVO:
    """
    Retrieve available workflow functions (activities).
    
    Functions are the core actions that can be performed in workflow nodes. They 
    take inputs and produce outputs that can be used by subsequent nodes. Only 
    active functions are returned.
    
    Returns:
        - activities (List[WorkflowActivityVO]): List of active workflow functions with input/output specifications
            - id: Optional[str] = ""
            - categoryId (str)
            - desc (str)
            - displayable Optional[str] = ""
            - name (str)
            - inputs [List[WorkflowInputsVO]]
            - outputs [List[WorkflowOutputsVO]]
            - status (str)

        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("list_workflow_activities: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_ACTIVITIES, "GET", ctx=ctx)
        logger.debug("workflow activities output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_functions")
        if error:
            logger.error("workflow activities error: {}\n".format(output))
            return vo.WorkflowActivityListVO(error=error)
        
        activities: List[vo.WorkflowActivityVO]=[]
        for item in output["items"]:
            if "displayable" in item and item.get("status") == "Active":
                activities.append(vo.WorkflowActivityVO.model_validate(item))
        
        logger.debug("modified activities: {}\n".format(vo.WorkflowActivityListVO(activities=activities).model_dump()))

        return vo.WorkflowActivityListVO(activities=activities)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow activities: {}\n".format(e))
        return vo.WorkflowActivityListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_functions"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Rules",read_only=True))
async def list_workflow_rules(ctx: Context | None = None) -> vo.WorkflowRuleListVO:
    """
    Retrieve available workflow rules.
    
    Rules are predefined logic that can be executed in workflow nodes. They typically 
    handle data processing, validation, or business logic. Rules have inputs and 
    outputs that can be mapped to other workflow components.
    
    Returns:
        - rules (List[WorkflowRuleVO]): List of available workflow rules with input/output specifications
            - id (str)
            - name: (str)
            - description (str)
            - ruleInputs: [List[WorkflowRuleInputsVO]]
            - ruleOutputs: [List[WorkflowRuleOutputsVO]]

        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("list_workflow_prebuild_rules: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_PREBUILD_RULES, "GET", {
            "type": "rule",
            "meta_tags": "MCP",
        }, ctx=ctx)
        logger.debug("workflow rules output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_rules")
        if error:
            logger.error("workflow rules error: {}\n".format(output))
            return vo.WorkflowRuleListVO(error=error)
        
        for item in output.get("items", []):
            if "ruleInputs" in item and isinstance(item["ruleInputs"], dict):
                item["ruleInputs"] = list(item["ruleInputs"].values())

            if "ruleOutputs" in item and isinstance(item["ruleOutputs"], dict):
                outputs = item["ruleOutputs"]
                transformed_rule_outputs = []
                for key, value in outputs.items():
                    if isinstance(value, dict) and not value:
                        transformed_rule_outputs.append({"name": key})
                    else:
                        transformed_rule_outputs.append(value)
                item["ruleOutputs"] = transformed_rule_outputs

        logger.error("Transformed rules output: {}\n".format(output))

        rules: List[vo.WorkflowRuleVO]=[]
        for item in output["items"]:
            if "name" in item:
                rules.append(vo.WorkflowRuleVO.model_validate(item))
        
        logger.debug("modified rules: {}\n".format(vo.WorkflowRuleListVO(rules=rules).model_dump()))

        return vo.WorkflowRuleListVO(rules=rules)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow rules: {}\n".format(e))
        return vo.WorkflowRuleListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_rules"))

@mcp.tool(annotations=utils.tool_annotations("Fetch Workflow Rule",read_only=True))
async def fetch_workflow_rule(name: str, ctx: Context | None = None) -> vo.WorkflowRuleListVO:
    """
    Retrieve a specific workflow rule by name.
    
    Finds and returns the single workflow rule that matches the provided name. This rule
    contains the input/output specifications needed for workflow operations.
    
    Args:
        name (str): The name of the workflow rule to retrieve
        
    Returns:
        - rules (List[WorkflowRuleVO]): List containing the single matched workflow rule with input/output specifications
            - id: (str)
            - name: (str) 
            - description: (str)
            - ruleInputs: [List[WorkflowRuleInputsVO]]
            - ruleOutputs: [List[WorkflowRuleOutputsVO]]

        - error (Optional[str]): An error message if any issues occurred during retrieval.
    """
    try:
        logger.info(f"fetch_workflow_rule: searching for rule '{name}'\n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_PREBUILD_RULES, "GET", {
            "name": name,
        }, ctx=ctx)
        logger.debug("workflow rule output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "fetch_workflow_rule")
        if error:
            logger.error("workflow rule error: {}\n".format(output))
            return vo.WorkflowRuleListVO(error=error)
        
        for item in output.get("items", []):
            if "ruleInputs" in item and isinstance(item["ruleInputs"], dict):
                item["ruleInputs"] = list(item["ruleInputs"].values())

            if "ruleOutputs" in item and isinstance(item["ruleOutputs"], dict):
                outputs = item["ruleOutputs"]
                transformed_rule_outputs = []
                for key, value in outputs.items():
                    if isinstance(value, dict) and not value:
                        transformed_rule_outputs.append({"name": key})
                    else:
                        transformed_rule_outputs.append(value)
                item["ruleOutputs"] = transformed_rule_outputs

        if output.get("items") and len(output["items"]) > 0:
            item = output["items"][0]
            rule = vo.WorkflowRuleVO.model_validate(item)
            logger.debug("retrieved workflow rule: {}\n".format(rule.model_dump()))
            return vo.WorkflowRuleListVO(rules=[rule])
        
        logger.warning(f"No workflow rule returned for name: {name}")
        return vo.WorkflowRuleListVO(error=utils.build_structured_error(f"No workflow rule returned for name: {name}", "fetch_workflow_rule"))

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("fetch_workflow_rule error: {}\n".format(e))
        return vo.WorkflowRuleListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "fetch_workflow_rule"))

@mcp.tool(annotations=utils.tool_annotations("Fetch Task Readme",read_only=True))
async def fetch_task_readme(name: str, ctx: Context | None = None) -> vo.TaskReadmeResponseVO:
    """
    Retrieve README documentation for a specific task by name.
    
    Fetches the complete README documentation for a task, providing 
    detailed information about the task's purpose, usage instructions, prerequisites, 
    and implementation steps. This is useful for understanding how to properly use 
    a task in workflows.
    
    Args:
        name (str): The exact name of the task to retrieve README for
        
    Returns:
        - readmeText (str): Complete README documentation as readable text
        - taskName (str): Name of the task for reference
        - error (str): Error message if retrieval fails or README not available
    """
    try:
        logger.info(f"fetch_task_readme: searching for task '{name}'\n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_FETCH_TASK_README, "GET", {
            "name": name,
        }, ctx=ctx)
        logger.debug("task readme output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "fetch_task_readme")
        if error:
            logger.error("task readme error: {}\n".format(output))
            return vo.TaskReadmeResponseVO(taskName=name, error=error)
        
        if not output.get("items") or len(output["items"]) == 0:
            logger.warning(f"No task found with name: {name}")
            return vo.TaskReadmeResponseVO(taskName=name, error=utils.build_structured_error(f"Task '{name}' not available", "fetch_task_readme"))
        
        task_item = output["items"][0]
        task_name = task_item.get("name", name)
        readme_data = task_item.get("readmeData", "")
        
        if not readme_data:
            logger.warning(f"No README data found for task: {name}")
            return vo.TaskReadmeResponseVO(taskName=task_name, error=utils.build_structured_error(f"README not available for task: {name}", "fetch_task_readme"))
        
        try:
            readme_text = base64.b64decode(readme_data).decode('utf-8')
            logger.debug(f"Successfully decoded README for task: {task_name}")
            return vo.TaskReadmeResponseVO(readmeText=readme_text, taskName=task_name)
        except Exception as decode_error:
            logger.error(f"Failed to decode README data for task {name}: {decode_error}")
            return vo.TaskReadmeResponseVO(taskName=task_name, error=utils.build_structured_error(f"Failed to decode README data for task: {name}", "fetch_task_readme"))

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("fetch_task_readme error: {}\n".format(e))
        return vo.TaskReadmeResponseVO(taskName=name, error=utils.build_structured_error(f"Unexpected error: {e}", "fetch_task_readme"))

@mcp.tool(annotations=utils.tool_annotations("Fetch Rule Readme",read_only=True))
async def fetch_rule_readme(name: str, ctx: Context | None = None) -> vo.RuleReadmeResponseVO:
    """
    Retrieve README documentation for a specific rule by name.
    
    Fetches the complete README documentation for a rule, providing 
    detailed information about the rule's purpose, usage instructions, prerequisites, 
    and implementation steps. This is useful for understanding how to properly use 
    a rule in workflows.
    
    Args:
        name (str): The exact name of the rule to retrieve README for
        
    Returns:
        - readmeText (str): Complete README documentation as readable text
        - ruleName (str): Name of the rule for reference
        - error (str): Error message if retrieval fails or README not available
    """
    try:
        logger.info(f"fetch_rule_readme: searching for rule '{name}'\n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_FETCH_RULE_README, "GET", {
            "name": name,
        }, ctx=ctx)
        logger.debug("rule readme output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "fetch_rule_readme")
        if error:
            logger.error("rule readme error: {}\n".format(output))
            return vo.RuleReadmeResponseVO(ruleName=name, error=error)
        
        if not output.get("items") or len(output["items"]) == 0:
            logger.warning(f"No rule found with name: {name}")
            return vo.RuleReadmeResponseVO(ruleName=name, error=utils.build_structured_error(f"Rule '{name}' not available", "fetch_rule_readme"))
        
        rule_item = output["items"][0]
        rule_name = rule_item.get("name", name)
        readme_hash = rule_item.get("readme", "")
        
        if not readme_hash:
            logger.warning(f"No README hash found for rule: {name}")
            return vo.RuleReadmeResponseVO(ruleName=rule_name, error=utils.build_structured_error(f"README not available for rule: {name}", "fetch_rule_readme"))
        
        try:
            readme_response = await utils.make_API_call_to_CCow_and_get_response(f"{constants.URL_FETCH_FILE_BY_HASH}/{readme_hash}", "GET", ctx=ctx)
            logger.debug(f"README fetch response for rule {rule_name}: {readme_response}")
            
            readme_error = utils.build_structured_error(readme_response, "fetch_rule_readme:content")
            if readme_error:
                logger.error(f"Failed to fetch README content for rule {name}: {readme_response}")
                return vo.RuleReadmeResponseVO(ruleName=rule_name, error=readme_error)
            
            readme_text = ""
            if isinstance(readme_response, dict):
                file_content = readme_response.get("FileContent", "")
                if file_content:
                    try:
                        readme_text = base64.b64decode(file_content).decode('utf-8')
                    except Exception:
                        readme_text = file_content
                else:
                    logger.warning(f"No FileContent found in response for rule: {name}")
                    return vo.RuleReadmeResponseVO(ruleName=rule_name, error=utils.build_structured_error(f"README not available for rule: {name}", "fetch_rule_readme"))
            elif isinstance(readme_response, str):
                readme_text = readme_response
            
            if not readme_text:
                logger.warning(f"No README content found for rule: {name}")
                return vo.RuleReadmeResponseVO(ruleName=rule_name, error=utils.build_structured_error(f"README not available for rule: {name}", "fetch_rule_readme"))
            
            logger.debug(f"Successfully fetched README for rule: {rule_name}")
            return vo.RuleReadmeResponseVO(readmeText=readme_text, ruleName=rule_name)
            
        except Exception as fetch_error:
            logger.error(f"Failed to fetch README content for rule {name}: {fetch_error}")
            return vo.RuleReadmeResponseVO(ruleName=rule_name, error=utils.build_structured_error(f"Failed to fetch README content for rule: {name}", "fetch_rule_readme"))

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("fetch_rule_readme error: {}\n".format(e))
        return vo.RuleReadmeResponseVO(ruleName=name, error=utils.build_structured_error(f"Unexpected error: {e}", "fetch_rule_readme"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Tasks",read_only=True))
async def list_workflow_tasks(ctx: Context | None = None) -> vo.WorkflowTaskListVO:
    """
    Retrieve available workflow tasks.
    
    Tasks are predefined operations that can be executed in workflow nodes. They 
    typically handle external integrations, notifications, or complex operations.
    Tasks have inputs and outputs that can be mapped to other workflow components.
    
    Returns:
        - tasks (List[WorkflowTaskVO]): List of available workflow tasks with input/output specifications
            - id (str)
            - name (str)
            - displayable (str)
            - description (str)
            - inputs: [List[WorkflowTaskInputsVO]]
            - outputs: [List[WorkflowTaskOutputsVO]]

        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("list_workflow_prebuild_tasks: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_PREBUILD_TASKS, "GET", {
            "tags": "MCP-WORKFLOW",
        }, ctx=ctx)
        logger.debug("workflow prebuild tasks output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_tasks")
        if error:
            logger.error("workflow prebuild tasks error: {}\n".format(output))
            return vo.WorkflowTaskListVO(error=error)

        tasks: List[vo.WorkflowTaskVO]=[]
        for item in output["items"]:
            if "name" in item:
                tasks.append(vo.WorkflowTaskVO.model_validate(item))
        
        logger.debug("modified tasks: {}\n".format(vo.WorkflowTaskListVO(tasks=tasks).model_dump()))

        return vo.WorkflowTaskListVO(tasks=tasks)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("prebuild tasks error: {}\n".format(e))
        return vo.WorkflowTaskListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_tasks"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Condition Categories",read_only=True))
async def list_workflow_condition_categories(ctx: Context | None = None) -> vo.WorkflowConditionCategoryListVO:
    """
    Retrieve available workflow condition categories.
    
    Condition categories help organize workflow decision points by type. This is 
    useful for filtering and selecting appropriate conditions when building workflows.
    
    Returns:
        - Condition categories (List[WorkflowConditionCategoryItemVO]): List of condition categories
            - name (str): Name of the category.
        - error (Optional[str]): An error message if any issues occurred during retrieval. 
    """
    try:
        logger.info("list_workflow_condition_categories: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_CONDITION_CATEGORIES, "GET", ctx=ctx)
        logger.debug("workflow condition categories output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_condition_categories")
        if error:
            logger.error("workflow condition categories error: {}\n".format(output))
            return vo.WorkflowConditionCategoryListVO(error=error)
        
        conditionCategories: List[vo.WorkflowConditionCategoryItemVO]=[]
        for item in output["items"]:
            if "displayable" in item:
                conditionCategories.append(vo.WorkflowConditionCategoryItemVO.model_validate(item))
        
        logger.debug("modified condition categories: {}\n".format(vo.WorkflowConditionCategoryListVO(conditionCategories=conditionCategories).model_dump()))

        return vo.WorkflowConditionCategoryListVO(conditionCategories=conditionCategories)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow condition categories: {}\n".format(e))
        return vo.WorkflowConditionCategoryListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_condition_categories"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Conditions",read_only=True))
async def list_workflow_conditions(ctx: Context | None = None) -> vo.WorkflowConditionListVO:
    """
    Retrieve available workflow conditions.
    
    Conditions are decision points in workflows that evaluate expressions or functions 
    to determine the flow path. They can use CEL expressions or predefined functions 
    to make branching decisions. Only active conditions are returned.
    
    Returns:
        - conditions (List[WorkflowConditionVO]): List of active workflow conditions with input/output specifications
            - categoryId (str)
            - desc (str)
            - displayable: (str)
            - inputs: [List[WorkflowInputsVO]]
            - outputs: [List[WorkflowOutputsVO]]
            - status: (str)

        - error (Optional[str]): An error message if any issues occurred during retrieval.
    """
    try:
        logger.info("list_workflow_conditions: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_CONDITIONS, "GET", ctx=ctx)
        logger.debug("workflow conditions output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_conditions")
        if error:
            logger.error("workflow conditions error: {}\n".format(output))
            return vo.WorkflowConditionListVO(error=error)
        
        conditions: List[vo.WorkflowConditionVO]=[]
        for item in output["items"]:
            if "displayable" in item and item.get("status") == "Active":
                conditions.append(vo.WorkflowConditionVO.model_validate(item))
        
        logger.debug("modified conditions: {}\n".format(vo.WorkflowConditionListVO(conditions=conditions).model_dump()))

        return vo.WorkflowConditionListVO(conditions=conditions)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow conditions: {}\n".format(e))
        return vo.WorkflowConditionListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_conditions"))

@mcp.tool(annotations=utils.tool_annotations("Fetch Workflow Resource Data",read_only=True))
async def fetch_workflow_resource_data(resource: str, ctx: Context | None = None) -> vo.WorkflowResourceDataVO:
    """
    Fetch workflow resource data for a given resource type.
    
    Resources provide dynamic data that can be used as inputs in workflow nodes. 
    This function retrieves available data for a specific resource type.
    
    Args:
        resource: The resource type to fetch data for. Resource options: USER_BLOCK
        
    Returns:
        List of resource data items or error message
    """
    try:
        logger.info("list_user_blocks: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_RESOURCE_DATA, "POST", {"resource": resource}, ctx=ctx)
        logger.debug("list_user_blocks outputs : {}\n".format(output))
        
        error = utils.build_structured_error(output, "fetch_workflow_resource_data")
        if error or "items" not in output:
            logger.error("list_user_blocks error: {}\n".format(output))
            return vo.WorkflowResourceDataVO(error=error or utils.build_structured_error("Missing items in response", "fetch_workflow_resource_data"))
        
        return vo.WorkflowResourceDataVO(items=output.get("items", []))
    
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("list_user_blocks error: {}\n".format(e))
        return vo.WorkflowResourceDataVO(error=utils.build_structured_error(f"Unexpected error: {e}", "fetch_workflow_resource_data"))

@mcp.tool(annotations=utils.tool_annotations("Create Workflow",read_only=False))
async def create_workflow(workflow_yaml: str, ctx: Context | None = None) -> vo.WorkflowCreateResponseVO:
    """
    Create a new workflow using YAML definition. Always display the workflow diagram. 
    Before creation confirm workflow name and creation with the user before executing this tool. 
    Later use 'modify_workflow' tool to update states, activities, conditions, and transitions.

    yaml struct:
    
    metadata:
        name:
        description:
        summary:
        mermaidDiagram:

    This function creates a workflow from a YAML specification.

    Create workflow (establishes the ID)
    Update summary (document what we're building)
    Update mermaid diagram (visualize the flow)
    Then modify workflow (implement the actual logic)
    
    Args:
        workflow_yaml: YAML string defining the workflow structure
        
    Returns:
        Success message with workflow ID or error message
    """
    try:
        logger.info("Creating workflow from YAML")
        logger.debug(f"Workflow YAML: {workflow_yaml}")

        workflow_name = ""
        workflow_description = ""
        try:
            parsed_yaml = yaml.safe_load(workflow_yaml) if isinstance(workflow_yaml, str) else workflow_yaml
            if isinstance(parsed_yaml, dict):
                metadata = parsed_yaml.get("metadata")
                if not isinstance(metadata, dict):
                    metadata = {}
                    parsed_yaml["metadata"] = metadata
                metadata["tags"] = {"Channel": ["MCP_HOST"]}
                workflow_name = metadata.get("name") or ""
                workflow_description = metadata.get("description") or ""
                workflow_yaml = yaml.safe_dump(parsed_yaml, sort_keys=False)
        except Exception:
            logger.warning("Failed to set MCP tags or extract metadata from workflow YAML; proceeding with defaults")

        # Create workflow configuration first
        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_CREATE,"POST",workflow_yaml,type="yaml", ctx=ctx)
        logger.debug("create workflow output: {}\n".format(output))

        if not (output and isinstance(output, dict) and output.get("status") and output["status"].get("id")):
            logger.error(f"Failed to create workflow: {output}")
            return vo.WorkflowCreateResponseVO(
                error=utils.build_structured_error(output, "create_workflow")
                or utils.build_structured_error(f"Failed to create workflow: {output}", "create_workflow")
            )

        workflow_id = output["status"]["id"]

        logger.info(f"Workflow created successfully with ID: {workflow_id}")

        # Build UI URL
        try:
            base_host = constants.host.rstrip("/api") if hasattr(constants, "host") and isinstance(constants.host, str) else getattr(constants, "host", "")
            ui_url = f"{base_host}/ui/workflow-config/{workflow_id}" if base_host else ""
        except Exception:
            ui_url = ""

        logger.info(f"Workflow created URL : {ui_url}")
        
        # Create Workflow Specification 
        spec_payload = {
            "metadata": {
                "name": workflow_name,
                "description": workflow_description,
                "tags":{
                    "Channel":["MCP_HOST"]
                }
            },
            "spec": {
                "resources": [
                    {
                        "type": "GENERIC",
                        "includes": [],
                        "excludes": [],
                    }
                ],
                "reviewers": {"references": []},
                "approvers": {"references": []},
            },
        }

        spec_resp = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_SPECS, "POST", spec_payload, ctx=ctx)
        logger.debug("create workflow spec output: {}\n".format(spec_resp))

        spec_id = None
        if isinstance(spec_resp, dict) and spec_resp.get("status") and spec_resp["status"].get("id"):
            spec_id = spec_resp["status"]["id"]
            logger.info(f"Workflow spec created successfully with ID: {spec_id}")
        else:
            logger.error(f"Failed to create workflow spec: {spec_resp}")

        # If spec creation failed, return summary without attempting binding
        if not spec_id:
            msg = f"Workflow created (ID: {workflow_id})."
            if ui_url:
                msg += f" UI: {ui_url}"
            return vo.WorkflowCreateResponseVO(
                workflowId=workflow_id,
                uiUrl=ui_url,
                message=msg,
            )

        # Create Workflow Binding using the same name/description
        binding_payload = {
            "metadata": {
                "name": workflow_name,
                "description": workflow_description,
                "tags":{
                    "Channel":["MCP_HOST"]
                }
            },
            "spec": {
                "workflowResourceSpec": workflow_name,
                "workflowConfiguration": "",
                "workflowAdvancedConfig": workflow_name,
                "reviewers": {"references": []},
                "approvers": {"references": []},
            },
        }

        binding_resp = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_BINDINGS, "POST", binding_payload, ctx=ctx)
        logger.debug("create workflow binding output: {}\n".format(binding_resp))

        binding_id = None
        if isinstance(binding_resp, dict) and binding_resp.get("status") and binding_resp["status"].get("id"):
            binding_id = binding_resp["status"]["id"]
            logger.info(f"Workflow binding created successfully with ID: {binding_id}")
        else:
            logger.error(f"Failed to create workflow binding: {binding_resp}")

        # Build final message summarizing all creations
        if not binding_id:
            msg = f"Workflow created (ID: {workflow_id})."
            if ui_url:
                msg += f" UI: {ui_url}"
            return vo.WorkflowCreateResponseVO(
                workflowId=workflow_id,
                uiUrl=ui_url,
                message=msg,
            )

        msg = f"Workflow created (ID: {workflow_id})."
        if ui_url:
            msg += f" UI: {ui_url}"
        return vo.WorkflowCreateResponseVO(
            workflowId=workflow_id,
            uiUrl=ui_url,
            message=msg,
        )

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("create_workflow: {}\n".format(e))
        return vo.WorkflowCreateResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "create_workflow"))

@mcp.tool(annotations=utils.tool_annotations("List Workflows",read_only=True))
async def list_workflows(ctx: Context | None = None) -> vo.WorkflowListResponseVO:
    """
    Retrieve a list of all available workflow configurations.
    
    Returns:
        - List of workflow configuration items : Each item contains workflow metadata
        - Error message (str): If retrieval fails or an error occurs
    
    """
    try:
        logger.info("list_workflows: \n")

        output = await utils.make_API_call_to_CCow_and_get_response("/v3/workflow-configs", "GET", {
            "fields": "meta",
        }, ctx=ctx)
        logger.debug("list_workflows output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflows")
        if error:
            logger.error("list_workflows error: {}\n".format(output))
            return vo.WorkflowListResponseVO(error=error)
        if "items" in output:
            for item in output["items"]:
                utils.trimWorkflowDetails(item)
                # utils.deleteKey(item,"domainId")
                # utils.deleteKey(item,"orgId")
                # utils.deleteKey(item,"groupId")
                # utils.deleteKey(item,"spec")
                # if "status" in item:
                #     utils.deleteKey(item["status"],"filePathHash")
        # output["items"]=[]
        logger.debug("list_workflows output: {}\n".format(output))
        return vo.WorkflowListResponseVO(items=output["items"])
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("create_workflow: {}\n".format(e))
        return vo.WorkflowListResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflows"))


@mcp.tool(annotations=utils.tool_annotations("Get Workflow By Name",read_only=True))
async def get_workflow_by_name(name: str, ctx: Context | None = None) -> vo.WorkflowItemResponseVO:
    """
        Get a workflow configuration by its name (exact, case-sensitive match).

        Args:
            - name (str): workflow name to search
    """
    try:
        logger.info(f"get_workflow_by_name: {name}\n")

        output = await utils.make_API_call_to_CCow_and_get_response("/v3/workflow-configs", "GET", {
            "name": name,
        }, ctx=ctx)
        logger.debug("get_workflow_by_name output: {}\n".format(output))

        error = utils.build_structured_error(output, "get_workflow_by_name")
        if error:
            logger.error("get_workflow_by_name error: {}\n".format(output))
            return vo.WorkflowItemResponseVO(error=error)
        if "items" in output and isinstance(output["items"], list):
            for item in output["items"]:
                utils.trimWorkflowDetails(item, True)
            if len(output["items"]) > 0:
                return vo.WorkflowItemResponseVO(item=output["items"][0])
            return vo.WorkflowItemResponseVO(error=utils.build_structured_error("No workflow found with the given name", "get_workflow_by_name"))
        return vo.WorkflowItemResponseVO(error=utils.build_structured_error("Unexpected workflow lookup response", "get_workflow_by_name"))
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("get_workflow_by_name: {}\n".format(e))
        return vo.WorkflowItemResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "get_workflow_by_name"))

@mcp.tool(annotations=utils.tool_annotations("Fetch Workflow Details",read_only=True))
async def fetch_workflow_details(id:str, ctx: Context | None = None) -> vo.WorkflowItemResponseVO:
    """
        Args:
            - id (str): workflow id. This can be fetched from path /status/id of 'get_workflows' output
    """
    try:
        logger.info(f"fetch_workflow_details: {id}\n")

        output = await utils.make_API_call_to_CCow_and_get_response(f"/v3/workflow-configs/{id}", "GET", ctx=ctx)
        logger.debug("fetch_workflow_details output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "fetch_workflow_details")
        if error:
            logger.error("fetch_workflow_details error: {}\n".format(output))
            return vo.WorkflowItemResponseVO(error=error)
        return vo.WorkflowItemResponseVO(item=output)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("fetch_workflow_details: {}\n".format(e))
        return vo.WorkflowItemResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "fetch_workflow_details"))

@mcp.tool(annotations=utils.tool_annotations("Update Workflow Summary",read_only=False))
async def update_workflow_summary(id:str,summary:str, ctx: Context | None = None) -> vo.WorkflowMutationResponseVO:
    """
        Args:
            - id (str): workflow id. This can be fetched from path /status/id of 'get_workflows' output
            - summary (str): workflow summary, preferably ReadMe.
    """
    try:
        logger.info(f"update_workflow_summary: {id}, {summary}\n")

        req=[
            {
                "op":"add",
                "path": "/metadata/summary",
                "value": summary
            }
        ]
        output=await utils.make_API_call_to_CCow_and_get_response("/v3/workflow-configs/"+id,"PATCH",req, ctx=ctx)
        logger.debug("update_workflow_summary output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "update_workflow_summary")
        if error:
            logger.error("update_workflow_summary error: {}\n".format(output))
            return vo.WorkflowMutationResponseVO(error=error)
        return vo.WorkflowMutationResponseVO(success=True, message="Workflow summary updated", data=output)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("update_workflow_summary: {}\n".format(e))
        return vo.WorkflowMutationResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "update_workflow_summary"))

@mcp.tool(annotations=utils.tool_annotations("Update Workflow Mermaid Diagram",read_only=False))
async def update_workflow_mermaid_diagram(id:str,mermaidDiagram:str, ctx: Context | None = None) -> vo.WorkflowMutationResponseVO:
    """
        Args:
            - id (str): workflow id. This can be fetched from path /status/id of 'get_workflows' output
            - mermaidDiagram (str): workflow mermaid diagram
    """
    try:
        logger.info(f"update_workflow_mermaid_diagram: {id}, {mermaidDiagram}\n")

        req=[
            {
                "op":"add",
                "path": "/metadata/mermaidDiagram",
                "value": mermaidDiagram
            }
        ]
        output=await utils.make_API_call_to_CCow_and_get_response("/v3/workflow-configs/"+id,"PATCH",req, ctx=ctx)
        logger.debug("update_workflow_mermaid_diagram output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "update_workflow_mermaid_diagram")
        if error:
            logger.error("update_workflow_mermaid_diagram error: {}\n".format(output))
            return vo.WorkflowMutationResponseVO(error=error)
        return vo.WorkflowMutationResponseVO(success=True, message="Workflow mermaid diagram updated", data=output)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("update_workflow_mermaid_diagram: {}\n".format(e))
        return vo.WorkflowMutationResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "update_workflow_mermaid_diagram"))

@mcp.tool(annotations=utils.tool_annotations("Modify Workflow",read_only=False))
async def modify_workflow(workflow_yaml: str, workflow_id: str, ctx: Context | None = None) -> vo.WorkflowMutationResponseVO:
    """
    Modify an existing workflow using YAML definition.
    
    The workflow ID (UUID) is required to identify which workflow to modify. This 
    function updates an existing workflow with a new YAML specification. The YAML 
    should define the workflow structure including states, activities, conditions, 
    and transitions. Always display the workflow diagram and confirm with the 
    user before executing this tool.

    BEFORE using 'modify_workflow' tool, you MUST check:
    - Do I have the complete CCow workflow YAML schema?
    - Do I know the exact state configuration requirements?
    - Do I understand the data flow and variable reference patterns?
    If the answer to ANY of these is "no", respond with:
    "I need CCow workflow schema knowledge to properly implement this workflow. 
    Please provide the workflow YAML specification, state definitions, and 
    integration patterns before I proceed with modify_workflow."

    
    Args:
        workflow_yaml: YAML string defining the updated workflow structure
        workflow_id: ID of the workflow to modify
        
    Returns:
        Success message or error message
    """
    try:
        logger.info(f"Modifying workflow with ID: {workflow_id}")
        logger.debug(f"Updated workflow YAML: {workflow_yaml}")

        response =await utils.make_API_call_to_CCow_and_get_response(f"{constants.URL_WORKFLOW_CREATE}/{workflow_id}","PUT",workflow_yaml,type="yaml",return_raw=True, ctx=ctx)
        logger.debug("create workflow output: {}\n".format(response))

        if response.status_code == 502:
            return vo.WorkflowMutationResponseVO(error=utils.build_structured_error(error_constants.ERROR_BAD_GATEWAY, "modify_workflow"))

        if response.status_code == 204:
            logger.info("Workflow updated successfully")
            return vo.WorkflowMutationResponseVO(success=True, message="Workflow updated successfully")
        else:
            try:
                error_msg = response.json().get("ErrorMessage", response.text)
            except Exception:
                error_msg = response.text or f"HTTP {response.status_code}"
            logger.error(f"Failed to modify workflow: {error_msg}")
            return vo.WorkflowMutationResponseVO(error=utils.build_structured_error(f"Failed to update workflow: {error_msg}", "modify_workflow"))
    
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("modify_workflow: {}\n".format(e))
        return vo.WorkflowMutationResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "modify_workflow"))

@mcp.tool(annotations=utils.tool_annotations("List Workflow Predefined Variables",read_only=True))
async def list_workflow_predefined_variables(ctx: Context | None = None) -> vo.WorkflowPredefinedVariableListVO:
    """
    Retrieve available predefined variables for workflow configuration.
    
    Predefined variables are system-level variables that can be used in workflow 
    configurations. These system-level variables are mapped to specific operations. When you set a value for a predefined variable, 
    it automatically triggers the associated system operation (like sending workflow failure notifications).
    Example:
        - Sending workflow failure notifications to specific users
        - Sending workflow failure notifications to admin
    Returns:
        - items (List[WorkflowPredefinedVariableVO]): A list of predefined variables.
            - id (str): Unique identifier of the predefined variable
            - type (str): Data type of the variable (e.g., Text, Boolean)
            - name (str): Name of the predefined variable
        - error (Optional[str]): An error message if any issues occurred during retrieval.
    """
    try:
        logger.info("list_workflow_predefined_variables: \n")

        output = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_PREDEFINED_VARIABLES, "GET", ctx=ctx)
        logger.debug("workflow predefined variables output: {}\n".format(output))
        
        error = utils.build_structured_error(output, "list_workflow_predefined_variables")
        if error:
            logger.error(f"Failed to fetch predefined variables: {output}")
            return vo.WorkflowPredefinedVariableListVO(error=error)
        
        items = []
        for item in output.get("items", []):
            if "id" in item and "type" in item and "name" in item:
                items.append(vo.WorkflowPredefinedVariableVO.model_validate(item))
        
        logger.debug("modified predefined variables: {}\n".format(vo.WorkflowPredefinedVariableListVO(items=items).model_dump()))

        return vo.WorkflowPredefinedVariableListVO(items=items)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("workflow predefined variables: {}\n".format(e))
        return vo.WorkflowPredefinedVariableListVO(error=utils.build_structured_error(f"Unexpected error: {e}", "list_workflow_predefined_variables"))


@mcp.tool(annotations=utils.tool_annotations("Create Workflow Custom Event",read_only=False))
async def create_workflow_custom_event(
    displayable: str,
    desc: str,
    payload: List[vo.WorkflowCustomEventPayloadVO],
    categoryId: str = "7",
    eventType: str = "CUSTOM_EVENT",
    confirm: bool = False,
    ctx: Context | None = None
) -> vo.WorkflowCustomEventResponseVO:
    """
    Create a Workflow Catalog Custom Event.
    Show a preview of the event configuration and ask for user confirmation before proceeding.
    Only create the event after explicit confirmation from user (confirm=True)
    This tool validates payload item types against allowed values and requires explicit
    user confirmation before creating the event.

    Args:
        - displayable: Event display name
        - desc: Event description
        - categoryId: Event category identifier
        - payload: List of payload items. Each item must have {name, type, desc}
                   and type must be one of: Text, MultilineText, TextArray, DynamicTextArray,
                   Number, File, Boolean, Json
        - eventType: Event type. Default: "CUSTOM_EVENT"
        - confirm: Boolean flag. If False, will show a preview for user confirmation.
                  Only returns True after user explicitly accepts the preview.
    Returns:
        - Success or error message
    """
    try:
        logger.info("create_workflow_custom_event: validating inputs")

        sanitized_payload: List[dict] = []
        for idx, item in enumerate(payload):
            if not isinstance(item, vo.WorkflowCustomEventPayloadVO):
                try:
                    item = vo.WorkflowCustomEventPayloadVO.model_validate(item)
                except Exception:
                    return vo.WorkflowCustomEventResponseVO(error=utils.build_structured_error(f"Invalid payload item at index {idx}.", "create_workflow_custom_event"))

            sanitized_payload.append(item.model_dump())

        body_model = vo.WorkflowCustomEventCreateVO(
            displayable=displayable,
            desc=desc,
            categoryId=str(categoryId),
            payload=[vo.WorkflowCustomEventPayloadVO(**item) for item in sanitized_payload],
            type=eventType or "CUSTOM_EVENT",
        )
        body = body_model.model_dump()

        if not confirm:
            return vo.WorkflowCustomEventResponseVO(
                message="Confirmation required before creating event",
                preview=body,
                next_step="Re-run with confirm=True to create",
            )

        logger.info("create_workflow_custom_event: submitting request to API")
        output = await utils.make_API_call_to_CCow_and_get_response(
            constants.URL_WORKFLOW_EVENTS,
            "POST",
            body,
            ctx=ctx,
        )
        logger.debug("create_workflow_custom_event output: {}\n".format(output))

        if isinstance(output, str) or (isinstance(output, dict) and "id" not in output):
            logger.error(f"create_workflow_custom_event error: {output}")
            return vo.WorkflowCustomEventResponseVO(
                error=utils.build_structured_error(output, "create_workflow_custom_event")
                or utils.build_structured_error(f"Failed to create event: {output}", "create_workflow_custom_event")
            )

        created_id = output.get("id")

        if created_id:
            return vo.WorkflowCustomEventResponseVO(id=created_id, message="Workflow custom event created")

        return vo.WorkflowCustomEventResponseVO(error=utils.build_structured_error("Failed to create event", "create_workflow_custom_event"))

    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("create_workflow_custom_event: {}\n".format(e))
        return vo.WorkflowCustomEventResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "create_workflow_custom_event"))

@mcp.tool(annotations=utils.tool_annotations("Trigger Workflow",read_only=False))
async def trigger_workflow(
    workflowConfigId: str,
    event: str,
    inputs: dict | None = None,
    confirm: bool = False,
    ctx: Context | None = None
) -> vo.WorkflowTriggerResponseVO:
    """
    Trigger a workflow by the given workflow config id.
    
    Args:
        - workflowConfigId: The workflow config id 
        - event: Start event name.
        - inputs: Additional input payload for the event. IMPORTANT: Input values must be obtained from the user only - do not pass random/placeholder values. Each field requires meaningful user-provided values.
        - confirm: If False, shows a preview of required inputs and does not execute. If True, executes.

    Returns:
        - JSON string containing execution acknowledgement or error message
    """
    try:
        logger.info(f"trigger_workflow: workflowConfigId={workflowConfigId}, event={event}, inputs={inputs}, confirm={confirm}")

        query = {
            "workflow_advanced_config_id": workflowConfigId,
            "page": 1,
            "page_size": 1,
        }
        bindings_resp = await utils.make_API_call_to_CCow_and_get_response(
            f"{constants.URL_WORKFLOW_BINDINGS}", "GET", query, ctx=ctx
        )
        logger.debug(f"trigger_workflow bindings_resp: {bindings_resp}")

        binding_error = utils.build_structured_error(bindings_resp, "trigger_workflow:bindings")
        if binding_error or not isinstance(bindings_resp, dict) or not bindings_resp.get("items"):
            logger.error(f"Failed to resolve workflow binding: {bindings_resp}")
            return vo.WorkflowTriggerResponseVO(error=binding_error or utils.build_structured_error("Failed to execute workflow", "trigger_workflow:bindings"))

        item = bindings_resp["items"][0]
        status = item.get("status", {}) if isinstance(item, dict) else {}
        binding_id = status.get("id", "")

        if not binding_id:
            logger.error("No binding ID found in response")
            return vo.WorkflowTriggerResponseVO(error=utils.build_structured_error("Failed to execute workflow", "trigger_workflow"))

        exec_inputs = inputs.copy() if isinstance(inputs, dict) else {}
        if event and isinstance(event, str):
            exec_inputs["event"] = event
        if "event" not in exec_inputs or not isinstance(exec_inputs["event"], str) or not exec_inputs["event"].strip():
            logger.error("Missing or invalid event in inputs")
            return vo.WorkflowTriggerResponseVO(error=utils.build_structured_error("Starting event is required", "trigger_workflow"))

        required_fields: List[str] = []
        try:
            logger.info("Fetching workflow events to validate required fields")
            events_resp = await utils.make_API_call_to_CCow_and_get_response(constants.URL_WORKFLOW_EVENTS, "GET", ctx=ctx)

            if isinstance(events_resp, dict) and events_resp.get("items"):
                for ev in events_resp["items"]:
                    displayable = ev.get("displayable")
                    if isinstance(displayable, str) and displayable.strip() == exec_inputs["event"].strip():
                        payload_list = ev.get("payload") or []
                        for p in payload_list:
                            name = p.get("name") if isinstance(p, dict) else None
                            if isinstance(name, str) and name:
                                required_fields.append(name)
                        break
            logger.debug(f"Required fields for event: {required_fields}")
        except Exception as e:
            logger.error(f"Error fetching workflow events: {e}")
            required_fields = required_fields

        missing = []
        if required_fields:
            for f in required_fields:
                if f not in exec_inputs or exec_inputs.get(f) in [None, ""]:
                    missing.append(f)
            logger.debug(f"Missing required fields: {missing}")

        preview_body = {
            "workflowBindingId": binding_id,
            "input": exec_inputs,
        }

        if not confirm or missing:
            logger.info("Returning preview/validation response")
            return vo.WorkflowTriggerResponseVO(
                message="Confirmation required before executing workflow",
                event=exec_inputs.get("event"),
                requiredInputs=required_fields,
                provided={k: v for k, v in exec_inputs.items() if k != "event"},
                missing=missing,
                next_step="Provide missing inputs (if any) and re-run with confirm=True to execute",
            )

        body = {
            "workflowBindingId": binding_id,
            "input": exec_inputs,
        }

        logger.info(f"Executing workflow: {json.dumps(body)}")


        exec_resp = await utils.make_API_call_to_CCow_and_get_response(
            constants.URL_WORKFLOW_BINDINGS_EXECUTE, "POST", body, ctx=ctx
        )
        logger.debug(f"trigger_workflow exec_resp: {exec_resp}")

        exec_error = utils.build_structured_error(exec_resp, "trigger_workflow:execute")
        if exec_error:
            logger.error(f"Error response from execute API: {exec_resp}")
            return vo.WorkflowTriggerResponseVO(error=exec_error)

        logger.info("Workflow triggered successfully")
        return vo.WorkflowTriggerResponseVO(message="Workflow triggered successfully", result=exec_resp)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("trigger_workflow error: {}\n".format(e))
        return vo.WorkflowTriggerResponseVO(error=utils.build_structured_error(f"Unexpected error: {e}", "trigger_workflow"))
