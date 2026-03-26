import pytest

from constants import constants
from mcptypes import assistant_tool_types as vo
from mcptypes import workflow_tools_type as workflow_vo
from tools.assistant import assistant


class DummyRawResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.content = b"" if payload is None else b"payload"

    def json(self):
        if self._payload is None:
            raise ValueError("no payload")
        return self._payload


@pytest.mark.asyncio
async def test_create_assessment_returns_structured_response(monkeypatch, tool_fn):
    yaml_content = """
metadata:
  name: Security Plan
  categoryName: Cloud
planControls: []
"""

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_ASSESSMENT_CATEGORIES
        assert method == "GET"
        return [{"id": "cat-1", "name": "Cloud"}]

    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLANS
        assert method == "POST"
        assert payload["name"] == "Security Plan"
        assert payload["categoryId"] == "cat-1"
        return {"id": "plan-1", "name": "Security Plan"}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)
    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.create_assessment)(yaml_content)

    assert isinstance(result, vo.AssessmentCreateResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["data"] == {"id": "plan-1", "name": "Security Plan"}
    assert dumped["categoryName"] == "Cloud"
    assert dumped["error"] is None


@pytest.mark.asyncio
async def test_suggest_control_config_citations_returns_structured_items(monkeypatch, tool_fn):
    async def fake_post(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_GET_SIMILAR_CONTROLS
        assert method == "POST"
        assert request_body["assessment_id"] == "plan-1"
        return {
            "authorityDocument": "ISO 27001",
            "items": [
                {
                    "inputControlName": "Access Review",
                    "controlId": "ctrl-1",
                    "suggestions": [
                        {
                            "Name": "A.9.2.5",
                            "Control ID": "1001",
                            "Control Classification": "Preventive",
                            "Impact Zone": "Identity",
                            "Control Requirement": "Review access rights regularly",
                            "Sort ID": "9.2.5",
                            "Control Type": "Manual",
                            "Score": 0.92,
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.suggest_control_config_citations)(
        controlName="Access Review",
        assessmentId="plan-1",
        description="Review access rights",
        controlId="ctrl-1",
    )

    assert isinstance(result, vo.ControlCitationSuggestionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "items": [
            {
                "inputControlName": "Access Review",
                "controlId": "ctrl-1",
                "suggestions": [
                    {
                        "Name": "A.9.2.5",
                        "control_id": "1001",
                        "control_classification": "Preventive",
                        "impact_zone": "Identity",
                        "control_requirement": "Review access rights regularly",
                        "sort_id": "9.2.5",
                        "control_type": "Manual",
                        "score": 0.92,
                    }
                ],
            }
        ],
        "authorityDocument": "ISO 27001",
        "next_action": "attachToControl",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_assessments_returns_structured_items(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLANS
        assert method == "GET"
        assert request_body["category_name_contains"] == "Cloud"
        return {
            "items": [
                {"id": "plan-1", "name": "Security Plan", "categoryName": "Cloud"},
                {"id": "plan-2", "name": "Backup Plan", "categoryName": "Cloud"},
            ]
        }

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.list_assessments)(categoryName="Cloud")

    assert isinstance(result, vo.AssessmentListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "assessments": [
            {"id": "plan-1", "name": "Security Plan", "categoryName": "Cloud"},
            {"id": "plan-2", "name": "Backup Plan", "categoryName": "Cloud"},
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_assessment_control_configs_returns_structured_items(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_CONTROLS
        assert method == "GET"
        assert request_body["plan_id"] == "plan-1"
        return {
            "items": [
                {
                    "id": "ctrl-1",
                    "name": "Access Review",
                    "description": "Review access",
                    "alias": "AR-1",
                    "displayable": "1.1",
                    "context": {"owner": "IAM"},
                    "additionalContext": {"cadence": "monthly"},
                }
            ],
            "page": 1,
            "totalPage": 1,
        }

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.list_assessment_control_configs)("plan-1")

    assert isinstance(result, vo.AssessmentControlConfigListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "controls": [
            {
                "id": "ctrl-1",
                "name": "Access Review",
                "description": "Review access",
                "alias": "AR-1",
                "controlNumber": "1.1",
                "context": {"owner": "IAM"},
                "additionalContext": {"cadence": "monthly"},
            }
        ],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_fetch_control_source_summary_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_FETCH_SOURCE_SUMMARY
        assert method == "POST"
        assert payload == {"controlID": "ctrl-1"}
        return {
            "assessmentId": "plan-1",
            "assessmentName": "Security Plan",
            "controlId": "ctrl-1",
            "controlName": "Access Review",
            "lineage": [],
        }

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.fetch_control_source_summary)("ctrl-1")

    assert isinstance(result, vo.ControlSourceSummaryResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "assessmentId": "plan-1",
            "assessmentName": "Security Plan",
            "controlId": "ctrl-1",
            "controlName": "Access Review",
            "lineage": [],
        },
        "error": None,
        "next_action": "create sql query evidence",
        "next_step": None,
    }


@pytest.mark.asyncio
async def test_attach_citation_to_control_config_preview_returns_structured_response(tool_fn):
    result = await tool_fn(assistant.attach_citation_to_control_config)(
        assessmentId="plan-1",
        controlId="ctrl-1",
        authorityDocument="ISO 27001",
        controlIdsInAuthorityDocument=["1001"],
        sortId="9.2.5",
        controlNames=["Access Review"],
        confirm=False,
    )

    assert isinstance(result, vo.CitationAttachmentResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before attaching citation to control config",
        "assessmentId": "plan-1",
        "controlId": "ctrl-1",
        "citationDetails": {
            "authorityDocument": "ISO 27001",
            "controlIdsInAuthorityDocument": ["1001"],
            "sortId": "9.2.5",
            "controlNames": ["Access Review"],
        },
        "next_step": "Review the assessment, control config ID and citation details above. If correct, re-run with confirm=True to attach the citation.",
        "next_action": "Await for user confirmation",
        "citations": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_sql_query_evidence_preview_returns_structured_response(tool_fn):
    result = await tool_fn(assistant.create_sql_query_evidence)(
        controlConfigId="ctrl-1",
        sqlquery="select * from Snapshot",
        referedEvidenceNames=["Snapshot"],
        newEvidenceName="DerivedEvidence",
        confirm=False,
    )

    assert isinstance(result, vo.SqlQueryEvidenceMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before creating SQL query",
        "controlConfigId": "ctrl-1",
        "evidenceId": None,
        "sqlQuery": "select * from Snapshot",
        "newEvidenceName": "DerivedEvidence",
        "referedEvidenceNames": ["Snapshot"],
        "next_step": "Review the SQL query above. If you need to modify it, provide the updated sqlquery parameter when calling with confirm=True. If correct, re-run with confirm=True to create and attach the query.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_sql_query_evidence_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == f"{constants.URL_PLAN_CONTROLS}/ctrl-1/sql-query-evidences"
        assert method == "GET"
        return {
            "items": [
                {
                    "id": "sql-1",
                    "evidenceId": "evi-1",
                    "ruleId": "rule-1",
                    "sqlQuery": "select * from Snapshot",
                    "evidenceName": "DerivedEvidence",
                    "referedEvidenceNames": ["Snapshot"],
                }
            ]
        }

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.list_sql_query_evidence)("ctrl-1")

    assert isinstance(result, vo.SqlQueryEvidenceListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "evidences": [
            {
                "id": "sql-1",
                "evidenceId": "evi-1",
                "ruleId": "rule-1",
                "sqlQuery": "select * from Snapshot",
                "evidenceName": "DerivedEvidence",
                "referedEvidenceNames": ["Snapshot"],
            }
        ],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_sql_query_evidence_preview_returns_structured_response(tool_fn):
    result = await tool_fn(assistant.update_sql_query_evidence)(
        controlConfigId="ctrl-1",
        evidenceId="evi-1",
        sqlquery="select * from Snapshot where status = 'ok'",
        referedEvidenceNames=["Snapshot"],
        newEvidenceName="DerivedEvidence",
        confirm=False,
    )

    assert isinstance(result, vo.SqlQueryEvidenceMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before updating SQL query evidence",
        "controlConfigId": "ctrl-1",
        "evidenceId": "evi-1",
        "sqlQuery": "select * from Snapshot where status = 'ok'",
        "newEvidenceName": "DerivedEvidence",
        "referedEvidenceNames": ["Snapshot"],
        "next_step": "Review the updated SQL query above. If you need to modify it, provide the updated sqlquery parameter when calling with confirm=True. If correct, re-run with confirm=True to update the SQL query evidence.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_evidence_sample_data_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_FETCH_SAMPLE_EVIDENCE_DATA
        assert method == "POST"
        assert payload["controlID"] == "ctrl-1"
        return [{"evidenceName": "Snapshot", "sampleRecords": [{"id": 1}]}]

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.get_evidence_sample_data)("ctrl-1", ["Snapshot"], 2)

    assert isinstance(result, vo.EvidenceSampleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "controlId": "ctrl-1",
        "evidences": [{"evidenceName": "Snapshot", "sampleRecords": [{"id": 1}]}],
        "next_action": "create sql query",
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_entity_hierarchy_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_GET_ENTITY_HIERARCHY
        assert method == "GET"
        return {"entities": [{"class": "account", "name": "prod", "entities": []}]}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.get_entity_hierarchy)()

    assert isinstance(result, vo.EntityHierarchyResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {"entities": [{"class": "account", "name": "prod", "entities": []}]},
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_context_tables_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"entities": [{"class": "account", "name": "prod", "entities": [{"class": "region", "name": "us-east-1", "entities": []}]}]},
            {"additionalContext": {"entities": [{"class": "service", "name": "iam", "entities": []}]}}
        ]
    )

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return next(responses)

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.get_context_tables)("ctrl-1")

    assert isinstance(result, vo.ContextTablesResponseVO)
    assert result.model_dump() == {
        "success": True,
        "entity_hierarchy": {
            "headerRow": ["account", "region"],
            "dataRows": [["prod", "us-east-1"]],
        },
        "control_additional_context": {
            "headerRow": ["service"],
            "dataRows": [["iam"]],
        },
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_control_config_note_returns_preview_response(tool_fn):
    result = await tool_fn(assistant.create_control_config_note)(
        controlConfigId="ctrl-1",
        assessmentId="plan-1",
        notes="Document the SQL logic",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.NoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before creating note",
        "controlConfigId": "ctrl-1",
        "noteId": None,
        "topic": "Documentation",
        "notes": "Document the SQL logic",
        "next_step": "Review the Note above. If you need to modify it, provide the updated note parameter when calling with confirm=True. If correct, re-run with confirm=True to create note.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_control_config_notes_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_CONTROL_NOTES.format(controlConfigId="ctrl-1")
        assert method == "GET"
        return {"items": [{"id": "note-1", "topic": "Documentation", "notes": "Document the SQL logic"}]}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.list_control_config_notes)("ctrl-1")

    assert isinstance(result, vo.NoteListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "notes": [{"id": "note-1", "topic": "Documentation", "notes": "Document the SQL logic"}],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_control_config_note_returns_preview_response(tool_fn):
    result = await tool_fn(assistant.update_control_config_note)(
        controlConfigId="ctrl-1",
        noteId="note-1",
        assessmentId="plan-1",
        notes="Updated note",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.NoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before updating note",
        "controlConfigId": "ctrl-1",
        "noteId": "note-1",
        "topic": "Documentation",
        "notes": "Updated note",
        "next_step": "Review the updated Note above. If you need to modify it, provide the updated notes or topic parameters when calling with confirm=True. If correct, re-run with confirm=True to update the note.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_fetch_rule_readme_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"items": [{"name": "sql-rule", "readme": "hash-1"}]},
            {"FileContent": "IyBSRUFETUUKCnJ1bGUgZGV0YWlscw=="},
        ]
    )

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return next(responses)

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assistant.fetch_rule_readme)("sql-rule")

    assert isinstance(result, workflow_vo.RuleReadmeResponseVO)
    assert result.model_dump() == {
        "readmeText": "# README\n\nrule details",
        "ruleName": "sql-rule",
        "error": None,
    }


@pytest.mark.asyncio
async def test_validate_sql_query_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_VALIDATE_SQL_QUERY
        assert method == "POST"
        assert payload["assessmentID"] == "plan-1"
        assert payload["assessmentControlID"] == "ctrl-1"
        return {"queryStatus": "success", "data": {"columns": ["id"], "rows": [[1]]}}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.validate_sql_query)(
        sqlQuery="select * from Snapshot",
        referenceEvidences=[{"name": "Snapshot", "id": "run-evi-1"}],
        assessmentId="plan-1",
        controlId="ctrl-1",
    )

    assert isinstance(result, vo.SqlValidationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "resp": {"queryStatus": "success", "data": {"columns": ["id"], "rows": [[1]]}},
        "error": None,
    }


@pytest.mark.asyncio
async def test_mark_control_ready_for_execution_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_MARK_CONTROL_READY
        assert method == "POST"
        assert payload == {
            "assessmentId": "plan-1",
            "assessmentName": "Security Plan",
            "controlName": "Access Review",
            "primaryEvidenceName": "PrimaryEvidence",
            "supportingEvidenceName": "SupportingEvidence",
        }
        return {"status": "queued"}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.mark_control_ready_for_execution)(
        assessmentId="plan-1",
        assessmentName="Security Plan",
        controlName="Access Review",
        primaryEvidenceName="PrimaryEvidence",
        supportingEvidenceName="SupportingEvidence",
    )

    assert isinstance(result, vo.ReadyForExecutionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Control marked ready for execution",
        "response": {"status": "queued"},
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_control_config_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_ADD_CONTROL_OBJECTIVE
        assert method == "POST"
        assert payload["assessmentName"] == "Security Plan"
        return {"id": "plan-1"}

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(assistant.create_control_config)(
        assessmentName="Security Plan",
        controlObjectiveName="Access Review",
        controlObjectiveDescription="Review access rights",
        controlObjectiveCategory="Identity",
        entityClass="account",
        entities=["prod"],
        controlContext="IAM review flow",
    )

    assert isinstance(result, vo.CustomControlConfigResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {"assessment_id": "plan-1"},
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_control_config_contexts_returns_structured_response(monkeypatch, tool_fn):
    async def fake_patch(url, method, payload, return_raw=False, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/ctrl-1"
        assert method == "PATCH"
        assert return_raw is True
        assert payload == [
            {"op": "replace", "path": "/context", "value": "IAM review flow"},
            {
                "op": "replace",
                "path": "/additionalContext",
                "value": {"entities": [{"name": "prod", "class": "account"}]},
            },
        ]
        return DummyRawResponse(204)

    monkeypatch.setattr(assistant.utils, "make_API_call_to_CCow_and_get_response", fake_patch)

    result = await tool_fn(assistant.update_control_config_contexts)(
        controlConfigId="ctrl-1",
        entityClass="account",
        entities=["prod"],
        controlContext="IAM review flow",
    )

    assert isinstance(result, vo.UpdateControlContextsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "controlConfigId": "ctrl-1",
        "message": "Control config context and additional context updated successfully",
        "error": None,
    }
