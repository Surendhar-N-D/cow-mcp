from types import SimpleNamespace

import pytest

from constants import constants
from mcptypes import assessment_run_tool_types as vo
from tools.assessments.run import run


def _action_items():
    return {
        "items": [
            {
                "actionName": "Create ticket",
                "actionDescription": "Creates a support ticket",
                "actionSpecID": "spec-1",
                "actionBindingID": "binding-1",
                "target": "control",
                "rules": [{"ruleInputs": {"summary": "Ticket title", "internal__": "ignore"}}],
            }
        ]
    }


def _assessment_run_item():
    return {
        "id": "run-1",
        "name": "Run 1",
        "description": "desc",
        "planId": "plan-1",
        "applicationType": "generic",
        "configId": "cfg-1",
        "fromDate": "02/01/2026 00:00:00",
        "toDate": "02/17/2026 00:00:00",
        "started": "02/17/2026 09:52:03",
        "ended": "0001-01-01T00:00:00Z",
        "status": "Completed",
        "computedScore": 80,
        "computedWeight": 100,
        "planExecutionSummary": "",
        "tags": {},
        "complianceStatus": "COMPLIANT",
        "complianceStatus__": "In Place",
        "complianceWeight__": 10.0,
        "totalWeight__": 10.0,
        "compliancePCT__": 80.0,
        "createdAt": "2026-03-02T10:00:00Z",
        "updatedAt": "2026-03-02T10:10:00Z",
        "inputs": {},
        "otherInfos": {},
        "scoreVersioningTimeStamp": "20260302100000",
        "complianceStatusThreshold": 100,
        "scoreColorThreshold": {
            "red": 15,
            "yellow": 75
        }
    }


def _control_item():
    return {
        "id": "ctrl-1",               
        "name": "Control 1",           
        "displayable": "AC-1",         
        "status": "Completed",         
        "description": "Sample control description",
        "alias": "AC-1",
        "priority": "Medium",
        "stage": "Control Owner",
        "activationStatus": "active",
        "type": "Detective",
        "leafControl": True,
        "executionStatus": "Completed",
        "complianceStatus": "COMPLIANT",
        "complianceStatus__": "Compliant",
        "compliancePCT__": 100,
        "complianceWeight__": 1,
        "userSelectedComplianceWeight__": 1,
        "dueDate": "2026-01-01",
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
        "planInstanceId": "plan-1",
        "controlId": "control-ref-1",
        "assignmentStack": [],
        "checkedOut": False,
        "hasOwnAttributeValues": False
    }

@pytest.mark.asyncio
async def test_fetch_recent_assessment_runs_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCES
        assert method == "GET"
        assert request_body == {"fields": "basic", "page": 1, "page_size": 10, "plan_id": "plan-1"}
        return {"items": [_assessment_run_item()]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_recent_assessment_runs)("plan-1")

    assert isinstance(result, vo.AssessmentRunListVO)
    assert result.model_dump()["assessmentRuns"][0]["assessmentId"] == "plan-1"


@pytest.mark.asyncio
async def test_fetch_assessment_runs_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCES
        assert method == "GET"
        assert request_body == {"fields": "basic", "page": 1, "page_size": 10, "plan_id": "plan-1"}
        return {"items": [_assessment_run_item()]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_assessment_runs)("plan-1", page=1, pageSize=10)

    assert isinstance(result, vo.AssessmentRunListVO)
    assert result.model_dump()["assessmentRuns"][0]["name"] == "Run 1"


@pytest.mark.asyncio
async def test_fetch_assessment_run_details_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCE_CONTROLS
        assert method == "GET"
        assert request_body == {"fields": "basic", "is_leaf_control": "true", "plan_instance_id": "run-1"}
        return {"items": [_control_item()]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_assessment_run_details)("run-1")

    assert isinstance(result, vo.ControlListVO)
    assert result.model_dump()["controls"][0]["controlNumber"] == "AC-1"


@pytest.mark.asyncio
async def test_fetch_assessment_run_leaf_controls_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return {"items": [_control_item()]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_assessment_run_leaf_controls)("run-1")

    assert isinstance(result, vo.ControlListVO)
    assert result.model_dump()["controls"][0]["name"] == "Control 1"


@pytest.mark.asyncio
async def test_fetch_run_controls_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCE_CONTROLS
        assert method == "GET"
        assert request_body == {"fields": "basic", "control_name_contains": "Access", "page": 1, "page_size": 50}
        return {"items": [_control_item()]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_run_controls)("Access")

    assert isinstance(result, vo.ControlListVO)
    assert result.model_dump()["controls"][0]["id"] == "ctrl-1"


@pytest.mark.asyncio
async def test_fetch_run_control_meta_data_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == f"{constants.URL_PLAN_INSTANCE_CONTROLS}/ctrl-1/plan-data"
        assert method == "GET"
        return {
            "planId": "plan-1",
            "planName": "SOC 2",
            "planInstanceId": "run-1",
            "planInstanceName": "Run 1",
            "planInstanceControlId": "ctrl-1",
            "planInstanceControlName": "Access control",
            "planInstanceControlDisplayable": "AC-1",
        }

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_run_control_meta_data)("ctrl-1")

    assert isinstance(result, vo.ControlMetadataVO)
    assert result.model_dump()["controlNumber"] == "AC-1"


@pytest.mark.asyncio
async def test_fetch_assessment_run_leaf_control_evidence_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCE_EVIDENCES
        assert method == "GET"
        assert request_body == {"plan_instance_control_id": "ctrl-1"}
        return {"items": [{"id": "ev-1", "name": "Evidence A", "status": "Completed", "evidenceFileInfos": [{}]}]}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_assessment_run_leaf_control_evidence)("ctrl-1")

    assert isinstance(result, vo.ControlEvidenceListVO)
    assert result.model_dump()["evidences"][0]["name"] == "Evidence A"


@pytest.mark.asyncio
async def test_fetch_controls_positive(monkeypatch, tool_fn):
    async def fake_fetch_unique_node_data_and_schema(question):
        assert question == "Access"
        return SimpleNamespace(
            unique_property_values="Control.unique_values",
            neo4j_schema="(:Control)-[:HAS_CHILD]->(:Control)",
        )
    
    monkeypatch.setattr(run.graphdb.fetch_unique_node_data_and_schema, "fn", fake_fetch_unique_node_data_and_schema)

    result = await tool_fn(run.fetch_controls)("Access")

    assert isinstance(result, vo.ControlPromptVO)
    assert "HAS_CHILD" in result.model_dump()["prompt"]


@pytest.mark.asyncio
async def test_fetch_evidence_records_positive(monkeypatch, encode_json, tool_fn):
    payload = [
        {
            "id": "record-1",
            "System": "AWS",
            "Source": "scanner",
            "ResourceID": "i-123",
            "ResourceName": "instance-1",
            "ResourceType": "EC2",
            "ComplianceStatus": "COMPLIANT",
            "ComplianceReason": "Encrypted",
            "CreatedAt": "2026-03-24T10:00:00Z",
            "extraField": "kept",
        }
    ]

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_DATAHANDLER_FETCH_DATA
        assert method == "POST"
        assert request_body["evidenceID"] == "ev-1"
        return {"fileBytes": encode_json(payload)}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_evidence_records)("ev-1")

    assert isinstance(result, vo.RecordListVO)
    result_data = result.model_dump()
    assert result_data["totalRecords"] == 1
    assert result_data["records"][0]["otherInfo"] == {"id": "record-1", "extraField": "kept"}


@pytest.mark.asyncio
async def test_fetch_evidence_record_schema_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_DATAHANDLER_FETCH_DATA
        assert method == "POST"
        return {"config": {"srcConfig": [{"name": "System", "type": "string"}]}}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_evidence_record_schema)("ev-1")

    assert isinstance(result, vo.RecordSchemaListVO)
    assert result.model_dump()["recordSchema"][0]["name"] == "System"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function_name", "kwargs", "expected_payload"),
    [
        (
            "fetch_available_control_actions",
            {
                "assessmentName": "SOC 2",
                "controlNumber": "AC-1",
                "controlAlias": "Access control",
                "evidenceName": "Evidence A",
            },
            {
                "actionType": "action",
                "assessmentName": "SOC 2",
                "controlNumber": "AC-1",
                "controlAlias": "Access control",
                "evidenceName": "Evidence A",
                "isRulesReq": True,
                "triggerType": "userAction",
            },
        ),
        (
            "fetch_assessment_available_actions",
            {"name": "SOC 2"},
            {
                "actionType": "action",
                "assessmentName": "SOC 2",
                "isRulesReq": True,
                "triggerType": "userAction",
            },
        ),
        (
            "fetch_evidence_available_actions",
            {
                "assessment_name": "SOC 2",
                "control_number": "AC-1",
                "control_alias": "Access control",
                "evidence_name": "Evidence A",
            },
            {
                "actionType": "action",
                "assessmentName": "SOC 2",
                "controlNumber": "AC-1",
                "controlAlias": "Access control",
                "evidenceName": "Evidence A",
                "isRulesReq": True,
                "triggerType": "userAction",
            },
        ),
        (
            "fetch_general_available_actions",
            {"type": "control"},
            {
                "actionType": "action",
                "targetType": "control",
                "isRulesReq": True,
                "triggerType": "userAction",
            },
        ),
    ],
)
async def test_action_listing_tools_positive(monkeypatch, tool_fn, function_name, kwargs, expected_payload):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == expected_payload
        assert url == constants.URL_FETCH_AVAILABLE_ACTIONS
        assert method == "POST"
        return _action_items()

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(getattr(run, function_name))(**kwargs)

    assert isinstance(result, vo.ActionsListVO)
    assert result.model_dump()["actions"][0]["ruleInputs"] == {"summary": "Ticket title"}


@pytest.mark.asyncio
async def test_fetch_automated_controls_of_an_assessment_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_CONTROLS
        assert method == "GET"
        assert request_body["plan_id"] == "plan-1"
        return {
            "items": [
                {
                    "id": "ctrl-1",
                    "displayable": "AC-1",
                    "alias": "Access control",
                    "activationStatus": "ACTIVE",
                    "planId": "plan-1",
                    "rule": {"name": "rule-1"},
                }
            ]
        }

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.fetch_automated_controls_of_an_assessment)("plan-1")

    assert isinstance(result, vo.AutomatedControlListVO)
    assert result.model_dump()["controls"][0]["ruleName"] == "rule-1"


@pytest.mark.asyncio
async def test_execute_action_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body["actionInputs"] == {"summary": {"name": "summary", "value": "Create a ticket"}}
        assert url == constants.URL_ACTIONS_EXECUTIONS
        assert method == "POST"
        return {"id": "execution-1"}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.execute_action)(
        assessmentId="plan-1",
        assessmentRunId="run-1",
        actionBindingId="binding-1",
        assessmentRunControlId="ctrl-1",
        assessmentRunControlEvidenceId="ev-1",
        evidenceRecordIds=["record-1"],
        inputs={"summary": "Create a ticket"},
    )

    assert isinstance(result, vo.TriggerActionVO)
    assert result.model_dump()["id"] == "execution-1"


@pytest.mark.asyncio
async def test_upload_evidence_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_LINK_EVIDENCE
        assert method == "POST"
        assert request_body["nonCSVFile"]["fileName"] == "evidence.txt"
        return {"id": "evidence-1"}

    monkeypatch.setattr(run.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(run.upload_evidence)(
        runId="run-1",
        runControlId="ctrl-1",
        fileBytes="ZmlsZQ==",
        fileName="evidence.txt",
    )

    assert isinstance(result, vo.UploadEvidenceVO)
    assert result.model_dump() == {
        "id": "evidence-1",
        "message": "Evidence 'evidence.txt' uploaded successfully",
        "error": None,
    }
