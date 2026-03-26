from types import SimpleNamespace

import pytest

from constants import constants
from mcptypes import workflow_tools_type as vo
from tools.workflow import workflow


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function_name", "url", "response", "expected_model", "field_name", "field_value"),
    [
        (
            "list_workflow_event_categories",
            constants.URL_WORKFLOW_EVENT_CATEGORIES,
            {"items": [{"type": "assessment", "displayable": "Assessment"}]},
            vo.WorkflowEventCategoryListVO,
            "eventCategories",
            "Assessment",
        ),
        (
            "list_workflow_function_categories",
            constants.URL_WORKFLOW_ACTIVITY_CATEGORIES,
            {"items": [{"displayable": "Notifications"}]},
            vo.WorkflowActivityCategoryListVO,
            "activityCategories",
            "Notifications",
        ),
        (
            "list_workflow_functions",
            constants.URL_WORKFLOW_ACTIVITIES,
            {
                "items": [
                    {
                        "id": "fn-1",
                        "categoryId": "cat-1",
                        "desc": "Send email",
                        "displayable": "Send Email",
                        "name": "send_email",
                        "inputs": [{"name": "to", "desc": "recipient", "type": "Text"}],
                        "outputs": [{"name": "status", "desc": "result", "type": "Text"}],
                        "status": "Active",
                    }
                ]
            },
            vo.WorkflowActivityListVO,
            "activities",
            "Send Email",
        ),
        (
            "list_workflow_tasks",
            f"{constants.URL_WORKFLOW_PREBUILD_TASKS}?tags=MCP-WORKFLOW",
            {
                "items": [
                    {
                        "id": "task-1",
                        "name": "notify",
                        "displayable": "Notify",
                        "description": "Send notification",
                        "inputs": [{"name": "to", "description": "recipient", "dataType": "Text", "required": True}],
                        "outputs": [{"name": "status", "description": "result", "dataType": "Text"}],
                    }
                ]
            },
            vo.WorkflowTaskListVO,
            "tasks",
            "notify",
        ),
        (
            "list_workflow_condition_categories",
            constants.URL_WORKFLOW_CONDITION_CATEGORIES,
            {"items": [{"displayable": "Validation"}]},
            vo.WorkflowConditionCategoryListVO,
            "conditionCategories",
            "Validation",
        ),
        (
            "list_workflow_conditions",
            constants.URL_WORKFLOW_CONDITIONS,
            {
                "items": [
                    {
                        "id": "cond-1",
                        "categoryId": "cat-1",
                        "desc": "Check value",
                        "name": "check_value",
                        "displayable": "Check Value",
                        "inputs": [{"name": "value", "desc": "input", "type": "Text"}],
                        "outputs": [{"name": "result", "desc": "output", "type": "Boolean"}],
                        "status": "Active",
                    }
                ]
            },
            vo.WorkflowConditionListVO,
            "conditions",
            "Check Value",
        ),
        (
            "list_workflow_predefined_variables",
            constants.URL_WORKFLOW_PREDEFINED_VARIABLES,
            {"items": [{"id": "var-1", "type": "Text", "name": "wf_failure_email", "desc": "failure email"}]},
            vo.WorkflowPredefinedVariableListVO,
            "items",
            "wf_failure_email",
        ),
    ],
)
async def test_workflow_catalog_tools_positive(monkeypatch, tool_fn, function_name, url, response, expected_model, field_name, field_value):
    async def fake_request(request_url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_url == url.split("?")[0] if "?" in url else url
        assert method == "GET"
        return response

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(getattr(workflow, function_name))()

    assert isinstance(result, expected_model)
    dumped = result.model_dump()
    items = dumped[field_name]
    target = items[0]
    if field_name == "items":
        assert target["name"] == field_value
    elif field_name == "tasks":
        assert target["name"] == field_value
    elif field_name == "activities":
        assert target["displayable"] == field_value
    elif field_name == "conditions":
        assert target["displayable"] == field_value
    else:
        assert target["displayable"] == field_value


@pytest.mark.asyncio
async def test_list_workflow_events_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_WORKFLOW_EVENTS
        assert method == "GET"
        return {
            "items": [
                {"id": "ev-1", "categoryId": "1", "desc": "System", "displayable": "Assessment Completed", "payload": [], "status": "Active", "type": "SYSTEM_EVENT"},
                {"id": "ev-2", "categoryId": "7", "desc": "Custom", "displayable": "Manual Trigger", "payload": [], "status": "Active", "type": "CUSTOM_EVENT"},
            ]
        }

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.list_workflow_events)()

    assert isinstance(result, vo.WorkflowEventListVO)
    dumped = result.model_dump()
    assert dumped["systemEvents"][0]["displayable"] == "Assessment Completed"
    assert dumped["customEvents"][0]["displayable"] == "Manual Trigger"


@pytest.mark.asyncio
async def test_list_workflow_activity_types_positive(tool_fn):
    result = await tool_fn(workflow.list_workflow_activity_types)()

    assert isinstance(result, vo.WorkflowActivityTypeListVO)
    assert result.model_dump()["activityTypes"] == [
        "Pre-build Function",
        "Pre-build Rule",
        "Pre-build Task",
        "Existing Workflow",
    ]


@pytest.mark.asyncio
async def test_list_workflow_rules_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_WORKFLOW_PREBUILD_RULES
        assert method == "GET"
        assert request_body == {"type": "rule", "meta_tags": "MCP"}
        return {
            "items": [
                {
                    "id": "rule-1",
                    "name": "check_access",
                    "description": "Check access",
                    "ruleInputs": {"value": {"name": "value", "description": "input", "type": "Text", "isrequired": True}},
                    "ruleOutputs": {"result": {}},
                    "appScopeName": "workflow",
                }
            ]
        }

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.list_workflow_rules)()

    assert isinstance(result, vo.WorkflowRuleListVO)
    dumped = result.model_dump()
    assert dumped["rules"][0]["ruleInputs"][0]["name"] == "value"
    assert dumped["rules"][0]["ruleOutputs"][0]["name"] == "result"


@pytest.mark.asyncio
async def test_fetch_workflow_rule_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_WORKFLOW_PREBUILD_RULES
        assert method == "GET"
        assert request_body == {"name": "check_access"}
        return {
            "items": [
                {
                    "id": "rule-1",
                    "name": "check_access",
                    "description": "Check access",
                    "ruleInputs": {"value": {"name": "value", "description": "input", "type": "Text", "isrequired": True}},
                    "ruleOutputs": {"result": {}},
                    "appScopeName": "workflow",
                }
            ]
        }

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.fetch_workflow_rule)("check_access")

    assert isinstance(result, vo.WorkflowRuleListVO)
    assert result.model_dump()["rules"][0]["name"] == "check_access"


@pytest.mark.asyncio
async def test_fetch_task_readme_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_FETCH_TASK_README
        assert method == "GET"
        assert request_body == {"name": "notify"}
        return {"items": [{"name": "notify", "readmeData": "IyBUYXNrIFJFQURNRQ=="}]}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.fetch_task_readme)("notify")

    assert isinstance(result, vo.TaskReadmeResponseVO)
    assert result.model_dump()["readmeText"] == "# Task README"


@pytest.mark.asyncio
async def test_fetch_rule_readme_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        if url == constants.URL_FETCH_RULE_README:
            assert request_body == {"name": "check_access"}
            return {"items": [{"name": "check_access", "readme": "hash-1"}]}
        assert url == f"{constants.URL_FETCH_FILE_BY_HASH}/hash-1"
        assert method == "GET"
        return {"FileContent": "IyBSdWxlIFJFQURNRQ=="}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.fetch_rule_readme)("check_access")

    assert isinstance(result, vo.RuleReadmeResponseVO)
    assert result.model_dump()["readmeText"] == "# Rule README"


@pytest.mark.asyncio
async def test_fetch_workflow_resource_data_positive(monkeypatch, tool_fn):
    async def fake_post(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"resource": "USER_BLOCK"}
        assert url == constants.URL_WORKFLOW_RESOURCE_DATA
        assert method == "POST"
        return {"items": [{"id": "user-1", "name": "Alice"}]}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(workflow.fetch_workflow_resource_data)("USER_BLOCK")

    assert isinstance(result, vo.WorkflowResourceDataVO)
    assert result.model_dump()["items"][0]["name"] == "Alice"


@pytest.mark.asyncio
async def test_create_workflow_positive(monkeypatch, tool_fn):
    responses = [
        {"status": {"id": "wf-1"}},
        {"status": {"id": "spec-1"}},
        {"status": {"id": "binding-1"}},
    ]

    async def fake_post(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert method == "POST"
        return responses.pop(0)

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    yaml_text = "metadata:\n  name: Demo Workflow\n  description: Demo\n"
    result = await tool_fn(workflow.create_workflow)(yaml_text)

    assert isinstance(result, vo.WorkflowCreateResponseVO)
    dumped = result.model_dump()
    assert dumped["workflowId"] == "wf-1"
    assert dumped["error"] is None


@pytest.mark.asyncio
async def test_list_workflows_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == "/v3/workflow-configs"
        assert method == "GET"
        assert request_body == {"fields": "meta"}
        return {"items": [{"metadata": {"name": "Demo"}, "status": {"id": "wf-1", "filePathHash": "secret"}, "domainId": "x"}]}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.list_workflows)()

    assert isinstance(result, vo.WorkflowListResponseVO)
    dumped = result.model_dump()
    assert dumped["items"][0]["metadata"]["name"] == "Demo"
    assert "domainId" not in dumped["items"][0]


@pytest.mark.asyncio
async def test_get_workflow_by_name_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == "/v3/workflow-configs"
        assert method == "GET"
        assert request_body == {"name": "Demo"}
        return {"items": [{"metadata": {"name": "Demo"}, "spec": {"states": []}, "status": {"id": "wf-1", "filePathHash": "secret"}}]}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.get_workflow_by_name)("Demo")

    assert isinstance(result, vo.WorkflowItemResponseVO)
    assert result.model_dump()["item"]["metadata"]["name"] == "Demo"


@pytest.mark.asyncio
async def test_fetch_workflow_details_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == "/v3/workflow-configs/wf-1"
        assert method == "GET"
        return {"status": {"id": "wf-1"}, "metadata": {"name": "Demo"}}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.fetch_workflow_details)("wf-1")

    assert isinstance(result, vo.WorkflowItemResponseVO)
    assert result.model_dump()["item"]["status"]["id"] == "wf-1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function_name", "arg_name", "arg_value", "expected_message"),
    [
        ("update_workflow_summary", "summary", "README", "Workflow summary updated"),
        ("update_workflow_mermaid_diagram", "mermaidDiagram", "graph TD; A-->B;", "Workflow mermaid diagram updated"),
    ],
)
async def test_workflow_patch_tools_positive(monkeypatch, tool_fn, function_name, arg_name, arg_value, expected_message):
    async def fake_patch(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert method == "PATCH"
        assert url == "/v3/workflow-configs/wf-1"
        return {"status": {"id": "wf-1"}}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_patch)

    result = await tool_fn(getattr(workflow, function_name))("wf-1", arg_value)

    assert isinstance(result, vo.WorkflowMutationResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["message"] == expected_message


@pytest.mark.asyncio
async def test_modify_workflow_positive(monkeypatch, tool_fn):
    async def fake_put(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert method == "PUT"
        return SimpleNamespace(status_code=204, text="")

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_put)

    result = await tool_fn(workflow.modify_workflow)("metadata:\n  name: Demo\n", "wf-1")

    assert isinstance(result, vo.WorkflowMutationResponseVO)
    assert result.model_dump()["message"] == "Workflow updated successfully"


@pytest.mark.asyncio
async def test_create_workflow_custom_event_positive(monkeypatch, tool_fn):
    async def fake_post(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert method == "POST"
        assert url == constants.URL_WORKFLOW_EVENTS
        return {"id": "event-1"}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    payload = [vo.WorkflowCustomEventPayloadVO(name="recordId", desc="record id", type=vo.EventPayloadTypeEnum.Text)]
    result = await tool_fn(workflow.create_workflow_custom_event)(
        displayable="Demo Event",
        desc="Event description",
        payload=payload,
        confirm=True,
    )

    assert isinstance(result, vo.WorkflowCustomEventResponseVO)
    assert result.model_dump()["id"] == "event-1"


@pytest.mark.asyncio
async def test_trigger_workflow_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        if url == constants.URL_WORKFLOW_EVENTS:
            assert method == "GET"
            assert request_body is None
            return {"items": [{"displayable": "Start Demo", "payload": [{"name": "recordId"}]}]}
        if url == constants.URL_WORKFLOW_BINDINGS:
            assert method == "GET"
            assert request_body == {
                "workflow_advanced_config_id": "wf-1",
                "page": 1,
                "page_size": 1,
            }
            return {"items": [{"status": {"id": "binding-1"}}]}
        assert method == "POST"
        assert url == constants.URL_WORKFLOW_BINDINGS_EXECUTE
        assert request_body == {
            "workflowBindingId": "binding-1",
            "input": {"recordId": "1", "event": "Start Demo"},
        }
        return {"status": "queued"}

    monkeypatch.setattr(workflow.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(workflow.trigger_workflow)(
        workflowConfigId="wf-1",
        event="Start Demo",
        inputs={"recordId": "1"},
        confirm=True,
    )

    assert isinstance(result, vo.WorkflowTriggerResponseVO)
    dumped = result.model_dump()
    assert dumped["message"] == "Workflow triggered successfully"
    assert dumped["result"]["status"] == "queued"
