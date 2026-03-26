import pytest

from constants import constants
from mcptypes import rule_type as vo
from tools.rules import rules


class DummyRawResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.content = b"" if payload is None else b"payload"

    def json(self):
        if self._payload is None:
            raise ValueError("no payload")
        return self._payload


def make_task(
    *,
    name="task-a",
    description="Task description",
    input_name="config",
    data_type="FILE",
    template_content='{"hello":"world"}',
    fmt="json",
    required=True,
    default_value="",
):
    return vo.TaskVO(
        name=name,
        displayName=name,
        version="1.0.0",
        description=description,
        type="primitive",
        tags=["primitive"],
        applicationType="nocredapp",
        inputs=[
            vo.TaskInputVO(
                name=input_name,
                description="Input description",
                dataType=data_type,
                defaultValue=default_value,
                showField=True,
                required=required,
                templateFile=template_content,
                format=fmt,
            )
        ],
        outputs=[vo.TaskOutputVO(name="result", description="Result", dataType="STRING")],
        appTags={"appType": ["nocredapp"]},
        readmeData="",
    )


@pytest.mark.asyncio
async def test_list_assets_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, ctx=None, **kwargs):
        assert url == constants.URL_ASSETS
        assert method == "GET"
        return {"items": [{"id": "asset-1", "name": "AWS"}, {"id": "asset-2", "name": "Azure"}]}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.list_assets)()

    assert isinstance(result, vo.AssetListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "assets": [{"id": "asset-1", "name": "AWS"}, {"id": "asset-2", "name": "Azure"}],
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_checks_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLANS}/asset-1/fetch-all-evidences"
        assert method == "POST"
        return {"items": [{"id": "check-1", "name": "PublicAccess", "planControlId": "ctrl-1"}]}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.list_checks)("asset-1")

    assert isinstance(result, vo.CheckListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "checks": [{"id": "check-1", "name": "PublicAccess", "controlId": "ctrl-1"}],
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_asset_control_hierarchy_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLANS}/asset-1"
        assert method == "GET"
        return {
            "planControls": [
                {
                    "id": "root-1",
                    "name": "Identity",
                    "planControls": [{"id": "leaf-1", "name": "MFA"}],
                }
            ]
        }

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.get_asset_control_hierarchy)("asset-1")

    assert isinstance(result, vo.AssetControlHierarchyResponseVO)
    assert result.model_dump() == {
        "success": True,
        "planControls": [
            {
                "id": "root-1",
                "name": "Identity",
                "planControls": [{"id": "leaf-1", "name": "MFA", "planControls": None}],
            }
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_add_check_to_asset_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, payload, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/add-control-and-check"
        assert method == "POST"
        assert payload["assetID"] == "asset-1"
        return {"id": "ctrl-1"}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.add_check_to_asset)("asset-1", "parent-1", "PublicAccess", "Check public access")

    assert isinstance(result, vo.AddCheckToAssetResponseVO)
    assert result.model_dump() == {
        "success": True,
        "controlId": "ctrl-1",
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_asset_and_check_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"id": "asset-1"},
            {
                "planControls": [
                    {
                        "id": "parent-1",
                        "planControls": [
                            {
                                "id": "ctrl-1",
                                "evidences": [{"id": "check-1"}],
                            }
                        ],
                    }
                ]
            },
        ]
    )

    async def fake_call(url, method, payload=None, ctx=None, **kwargs):
        return next(responses)

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.create_asset_and_check)(
        assetName="AWS",
        controlName="Identity",
        checkName="PublicAccess",
        checkDescription="Check public access",
    )

    assert isinstance(result, vo.CreateAssetAndCheckResponseVO)
    assert result.model_dump() == {
        "success": True,
        "response": {
            "assetId": "asset-1",
            "parentControlId": "parent-1",
            "controlId": "ctrl-1",
            "checkId": "check-1",
        },
        "error": None,
    }


@pytest.mark.asyncio
async def test_schedule_asset_execution_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_ASSESSMENT_SCHEDULE
        assert method == "POST"
        assert payload["assessmentId"] == "asset-1"
        return {"id": "schedule-1"}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.schedule_asset_execution)(
        assetId="asset-1",
        runPrefixName="Daily",
        description="Daily asset run",
        cronTab="TZ=Asia/Calcutta 0 0 * * *",
        controlPeriod="DAY",
        controlDuration=1,
    )

    assert isinstance(result, vo.ScheduleAssetExecutionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "scheduleId": "schedule-1",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_asset_schedules_returns_structured_response(monkeypatch, tool_fn):
    async def fake_get_with_payload(url, payload, ctx=None):
        assert url == constants.URL_ASSESSMENT_SCHEDULE
        assert payload == {"assessmentId": "asset-1"}
        return {
            "items": [
                {
                    "id": "schedule-1",
                    "name": "Daily",
                    "description": "Daily asset run",
                    "controlPeriod": {"period": "DAY", "duration": 1},
                    "cronTab": "TZ=Asia/Calcutta 0 0 * * *",
                    "status": "ACTIVE",
                }
            ]
        }

    monkeypatch.setattr(rules.utils, "make_GET_API_call_to_CCow_With_Payload", fake_get_with_payload)

    result = await tool_fn(rules.list_asset_schedules)("asset-1")

    assert isinstance(result, vo.AssetScheduleListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "items": [
            {
                "id": "schedule-1",
                "name": "Daily",
                "description": "Daily asset run",
                "controlPeriod": {"period": "DAY", "duration": 1},
                "cronTab": "TZ=Asia/Calcutta 0 0 * * *",
                "status": "ACTIVE",
            }
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_delete_asset_schedule_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, ctx=None, **kwargs):
        assert url == f"{constants.URL_ASSESSMENT_SCHEDULE}/schedule-1"
        assert method == "DELETE"
        return {}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.delete_asset_schedule)("schedule-1")

    assert isinstance(result, vo.DeleteAssetScheduleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "error": None,
    }


@pytest.mark.asyncio
async def test_suggest_control_config_citations_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(payload, url, ctx=None):
        assert url == constants.URL_GET_SIMILAR_CONTROLS
        assert payload["assessment_type"] == "asset"
        return {
            "authorityDocument": "CIS",
            "items": [
                {
                    "inputControlName": "MFA",
                    "controlId": "ctrl-1",
                    "suggestions": [
                        {
                            "Name": "CIS 1.1",
                            "Control ID": "1001",
                            "Control Classification": "Preventive",
                            "Impact Zone": "Identity",
                            "Control Requirement": "Enable MFA",
                            "Sort ID": "1.1",
                            "Control Type": "Manual",
                            "Score": 0.9,
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow", fake_post)

    result = await tool_fn(rules.suggest_control_config_citations)("MFA", "Enable MFA", "ctrl-1")

    assert isinstance(result, vo.ControlCitationSuggestionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "items": [
            {
                "inputControlName": "MFA",
                "controlId": "ctrl-1",
                "suggestions": [
                    {
                        "Name": "CIS 1.1",
                        "control_id": "1001",
                        "control_classification": "Preventive",
                        "impact_zone": "Identity",
                        "control_requirement": "Enable MFA",
                        "sort_id": "1.1",
                        "control_type": "Manual",
                        "score": 0.9,
                    }
                ],
            }
        ],
        "authorityDocument": "CIS",
        "next_action": "attachToControl",
        "error": None,
    }


@pytest.mark.asyncio
async def test_add_citation_to_asset_control_returns_structured_response(monkeypatch, tool_fn):
    async def fake_call(url, method, payload, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/ctrl-1/link-source-control"
        assert method == "POST"
        assert payload == {
            "citation": {
                "authorityDocument": "CIS",
                "controlsInAuthorityDocument": ["1001"],
            }
        }
        return {}

    monkeypatch.setattr(rules.utils, "make_API_call_to_CCow_and_get_response", fake_call)

    result = await tool_fn(rules.add_citation_to_asset_control)("ctrl-1", "CIS", "1001")

    assert isinstance(result, vo.AddCitationToAssetControlResponseVO)
    assert result.model_dump() == {
        "success": True,
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_control_note_returns_preview_response(tool_fn):
    result = await tool_fn(rules.create_control_note)(
        controlId="ctrl-1",
        assessmentId="asset-1",
        notes="Document automation logic",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.ControlNoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before creating note",
        "controlId": "ctrl-1",
        "noteId": None,
        "topic": "Documentation",
        "notes": "Document automation logic",
        "next_step": "Review the Note above. If you need to modify it, provide the updated note parameter when calling with confirm=True. If correct, re-run with confirm=True to create note.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_control_notes_returns_structured_response(monkeypatch, tool_fn):
    async def fake_get(url, ctx=None):
        assert url == constants.URL_PLAN_CONTROL_NOTES.format(controlConfigId="ctrl-1")
        return {"items": [{"id": "note-1", "topic": "Documentation", "notes": "Document automation logic"}]}

    monkeypatch.setattr(rules.utils, "make_GET_API_call_to_CCow", fake_get)

    result = await tool_fn(rules.list_control_notes)("ctrl-1")

    assert isinstance(result, vo.ControlNoteListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "notes": [{"id": "note-1", "topic": "Documentation", "notes": "Document automation logic"}],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_control_config_note_returns_preview_response(tool_fn):
    result = await tool_fn(rules.update_control_config_note)(
        controlId="ctrl-1",
        noteId="note-1",
        assessmentId="asset-1",
        notes="Updated note",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.ControlNoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before updating note",
        "controlId": "ctrl-1",
        "noteId": "note-1",
        "topic": "Documentation",
        "notes": "Updated note",
        "next_step": "Review the updated Note above. If you need to modify it, provide the updated notes or topic parameters when calling with confirm=True. If correct, re-run with confirm=True to update the note.",
        "error": None,
    }


def test_fetch_assessments_returns_structured_response(monkeypatch, tool_fn):
    def fake_get_assessments(params, ctx=None):
        assert params["category_name_contains"] == "Cloud"
        return [vo.AssessmentVO(id="plan-1", name="Security Plan", categoryName="Cloud")]

    monkeypatch.setattr(rules.rule, "get_assessments", fake_get_assessments)

    result = tool_fn(rules.fetch_assessments)(categoryName="Cloud")

    assert isinstance(result, vo.AssessmentListVO)
    assert result.model_dump() == {
        "success": True,
        "assessments": [{"id": "plan-1", "name": "Security Plan", "categoryName": "Cloud"}],
        "error": None,
    }


def test_fetch_leaf_controls_of_an_assessment_returns_structured_response(monkeypatch, tool_fn):
    def fake_get_controls(params, ctx=None):
        assert params["plan_id"] == "plan-1"
        return [vo.AssessmentControlVO(id="ctrl-1", name="MFA", alias="1.1", ruleId="")]

    monkeypatch.setattr(rules.rule, "get_assessment_controls", fake_get_controls)

    result = tool_fn(rules.fetch_leaf_controls_of_an_assessment)("plan-1")

    assert isinstance(result, vo.AssessmentControlListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "controls": [{"id": "ctrl-1", "name": "MFA", "alias": "1.1", "ruleId": ""}],
        "error": None,
    }


def test_verify_control_in_assessment_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "get_assessments",
        lambda params, ctx=None: [vo.AssessmentVO(id="plan-1", name="Security Plan", categoryName="Cloud")],
    )
    monkeypatch.setattr(
        rules.rule,
        "get_assessment_controls",
        lambda params, ctx=None: [vo.AssessmentControlVO(id="ctrl-1", name="MFA", alias="1.1", ruleId="")],
    )

    result = tool_fn(rules.verify_control_in_assessment)("Security Plan", "1.1")

    assert isinstance(result, vo.VerifyControlInAssessmentResponseVO)
    assert result.model_dump() == {
        "success": True,
        "assessment_name": "Security Plan",
        "control_alias": "1.1",
        "control_info": {"id": "ctrl-1", "name": "MFA", "alias": "1.1", "ruleId": ""},
        "warning": None,
        "message": "Leaf control '1.1' found and available for rule attachment.",
        "next_actions": None,
        "ready_for_attachment": True,
        "error": None,
    }


def test_check_applications_publish_status_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: [{"appName": "GitHub", "published": True}],
    )

    result = tool_fn(rules.check_applications_publish_status)([{"name": ["GitHub"]}])

    assert isinstance(result, vo.ApplicationsPublishStatusResponseVO)
    assert result.model_dump() == {
        "success": True,
        "app_info": [{"appName": "GitHub", "published": True}],
        "error": None,
    }


def test_check_rule_publish_status_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {"items": [{"id": "rule-1", "name": "MFA Rule"}]},
    )

    result = tool_fn(rules.check_rule_publish_status)("MFA Rule")

    assert isinstance(result, vo.RulePublishStatusResponseVO)
    assert result.model_dump() == {
        "success": True,
        "published": True,
        "rule_info": [{"id": "rule-1", "name": "MFA Rule"}],
        "message": "Rule 'MFA Rule' is already published",
        "error": None,
    }


def test_publish_application_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: [{"appName": "GitHub", "published": True}],
    )

    result = tool_fn(rules.publish_application)("MFA Rule", [{"appName": "GitHub"}])

    assert isinstance(result, vo.PublishApplicationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "published": True,
        "successful_apps": [{"appName": "GitHub", "published": True}],
        "failed_apps": [],
        "message": "All applications for rule 'MFA Rule' published successfully",
        "error": None,
    }


def test_verify_control_automation_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "get",
        lambda path, header: {"ruleId": "rule-1", "name": "MFA"},
    )
    monkeypatch.setattr(
        rules,
        "fetch_cc_rule_by_id",
        lambda rule_id, ctx=None: {
            "name": "MFA Rule",
            "type": "detective",
            "meta": {"description": "Checks MFA"},
        },
    )

    result = tool_fn(rules.verify_control_automation)("ctrl-1")

    assert isinstance(result, vo.ControlAutomationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "control_id": "ctrl-1",
        "control_name": "MFA",
        "automated": True,
        "rule_id": "rule-1",
        "rule_info": {
            "name": "MFA Rule",
            "type": "detective",
            "description": "Checks MFA",
        },
        "message": "This control is automated with the rule details provided above.",
        "error": None,
    }


def test_fetch_cc_rules_list_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"items": [{"id": "rule-1", "name": "MFA Rule", "meta": {"description": "Checks MFA"}}], "totalPage": 1}
        ]
    )
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.wsutils, "get", lambda path, params, header: next(responses))

    result = tool_fn(rules.fetch_cc_rules_list)({"page_size": 10})

    assert isinstance(result, vo.SimplifiedRuleListVO)
    assert result.model_dump() == {
        "success": True,
        "rules": [
            {
                "id": "rule-1",
                "name": "MFA Rule",
                "purpose": "",
                "description": "Checks MFA",
            }
        ],
        "error": None,
    }


def test_fetch_tasks_suggestions_returns_structured_response(monkeypatch, tool_fn):
    if not hasattr(rules, "fetch_tasks_suggestions"):
        pytest.skip("fetch_tasks_suggestions is disabled by configuration")

    monkeypatch.setattr(
        rules.rule,
        "fetch_rules_and_tasks_suggestions",
        lambda query, identifierType, ctx=None: {"items": [{"name": "TaskA"}]},
    )

    result = tool_fn(rules.fetch_tasks_suggestions)("need help", "summarized requirement")

    assert isinstance(result, vo.TaskSuggestionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {"items": [{"name": "TaskA"}]},
        "error": None,
    }


def test_create_support_ticket_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "create_support_ticket_api",
        lambda payload, ctx=None: {"ticketId": "ticket-1", "status": "created"},
    )

    result = tool_fn(rules.create_support_ticket)("Help", "<p>Issue</p>", "High")

    assert isinstance(result, vo.SupportTicketResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {"ticketId": "ticket-1", "status": "created"},
        "error": None,
    }


def test_get_applications_for_tag_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "get",
        lambda path, params, header: {
            "items": [
                {
                    "id": "app-1",
                    "credentialName": "GitHub App",
                    "appType": "github::",
                    "othersTags": {"purpose": ["source-repo"]},
                }
            ]
        },
    )

    result = tool_fn(rules.get_applications_for_tag)("github")

    assert isinstance(result, vo.ApplicationsForTagResponseVO)
    assert result.model_dump() == {
        "success": True,
        "tag_name": "github",
        "additional_tags": None,
        "applications": [
            {
                "id": "app-1",
                "name": "GitHub App",
                "appType": "github",
                "othersTags": {"purpose": ["source-repo"]},
            }
        ],
        "count": 1,
        "message": "Found 1 applications for tag 'github'. User can select an existing application or create new credentials.",
        "error": None,
    }


def test_attach_rule_to_control_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "attach_rule_to_control_api",
        lambda control_id, body, ctx=None: {"success": True, "evidenceInfo": {"id": "evi-1"}},
    )

    result = tool_fn(rules.attach_rule_to_control)("rule-1", "Security Plan", "ctrl-1", True)

    assert isinstance(result, vo.AttachRuleToControlResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_id": "rule-1",
        "rule_name": None,
        "assessment_name": "Security Plan",
        "control_id": "ctrl-1",
        "attachment_status": "attached",
        "evidence_created": True,
        "evidence_info": {"id": "evi-1"},
        "message": "Rule 'rule-1' successfully attached to control 'ctrl-1' in assessment 'Security Plan' with evidence created.",
        "error": None,
    }


def test_fetch_cc_rule_by_id_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "fetch_cc_rule_by_id",
        lambda rule_id, ctx=None: {"id": rule_id, "name": "MFA Rule"},
    )

    result = tool_fn(rules.fetch_cc_rule_by_id)("rule-1")

    assert isinstance(result, vo.RuleFetchResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_id": "rule-1",
        "rule_name": None,
        "data": {"id": "rule-1", "name": "MFA Rule"},
        "next_actions": None,
        "error": None,
    }


def test_fetch_cc_rule_by_name_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "fetch_cc_rule_by_name",
        lambda rule_name, ctx=None: {"id": "rule-1", "name": rule_name},
    )

    result = tool_fn(rules.fetch_cc_rule_by_name)("MFA Rule")

    assert isinstance(result, vo.RuleFetchResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_id": None,
        "rule_name": "MFA Rule",
        "data": {"id": "rule-1", "name": "MFA Rule"},
        "next_actions": None,
        "error": None,
    }


def test_publish_rule_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {
            "message": "Rule has been published successfully",
            "items": [{"id": "rule-1", "name": "MFA Rule"}],
            "ruleId": "rule-1",
        },
    )

    result = tool_fn(rules.publish_rule)("MFA Rule")

    assert isinstance(result, vo.PublishRuleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "published": True,
        "cc_rule_id": "rule-1",
        "rule_info": [{"id": "rule-1", "name": "MFA Rule"}],
        "message": "Rule 'MFA Rule' published successfully",
        "ui_display_message": "View your published rule on the ComplianceCow Rules Dashboard → /ui/rules-workflow",
        "error": None,
    }


def test_get_template_guidance_returns_structured_response(monkeypatch, tool_fn):
    task = make_task()
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(rules.rule, "decode_content", lambda content: '{"hello":"world"}')
    monkeypatch.setattr(rules.rule, "generate_detailed_template_guidance", lambda content, task_input: {"overview": "Use JSON"})
    monkeypatch.setattr(rules.rule, "generate_example_content", lambda content, fmt: '{"hello":"world"}')
    monkeypatch.setattr(rules.rule, "get_template_validation_rules", lambda fmt: {"syntax": "valid json"})

    result = tool_fn(rules.get_template_guidance)("task-a", "config")

    assert isinstance(result, vo.TemplateGuidanceResponseVO)
    assert result.model_dump() == {
        "success": True,
        "task_name": "task-a",
        "input_name": "config",
        "input_description": "Input description",
        "format": "json",
        "decoded_template": '{"hello":"world"}',
        "guidance": {"overview": "Use JSON"},
        "example_content": '{"hello":"world"}',
        "validation_rules": {"syntax": "valid json"},
        "presentation_format": "Now configuring: [X of Y inputs]\n\nTask: task-a\nInput: config - Input description\n\nHere's the template structure:\n\n{\"hello\":\"world\"}\n\nThis json file requires specific fields. Please provide your actual configuration following this template.",
        "error": None,
    }


def test_collect_template_input_returns_structured_response(monkeypatch, tool_fn):
    task = make_task()
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(rules.rule, "validate_template_content_enhanced", lambda task_input, user_content: {"valid": True, "errors": [], "suggestions": []})
    monkeypatch.setattr(rules.rule, "generate_content_preview", lambda content, fmt: '{"hello":"world"}')

    result = tool_fn(rules.collect_template_input)("task-a", "config", {"hello": "world"})

    assert isinstance(result, vo.CollectTemplateInputResponseVO)
    assert result.model_dump() == {
        "success": True,
        "task_name": "task-a",
        "input_name": "config",
        "validated_content": '{"hello": "world"}',
        "content_preview": '{"hello":"world"}',
        "needs_final_confirmation": True,
        "data_type": "FILE",
        "format": "json",
        "is_file_type": True,
        "final_confirmation_message": "You provided this JSON content:\n\n{\"hello\":\"world\"}\n\nIs this correct? (yes/no)",
        "message": "Template content validated - needs final confirmation before processing and rule update",
        "ready_for_rule_update": True,
        "validation_errors": None,
        "suggestions": None,
        "error": None,
    }


def test_confirm_template_input_returns_structured_response(monkeypatch, tool_fn):
    task = make_task()
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(
        rules.upload_file,
        "fn",
        lambda rule_name, file_name, content, ctx=None: vo.UploadFileResponseVO(success=True, file_url="https://files.example/config.json"),
    )
    monkeypatch.setattr(
        rules.fetch_rule,
        "fn",
        lambda rule_name, ctx=None: {"success": True, "rule_structure": {"spec": {"inputs": {}, "inputsMeta__": []}}},
    )
    monkeypatch.setattr(
        rules.create_rule,
        "fn",
        lambda rule_structure, ctx=None: {"success": True, "detected_status": "collecting_inputs", "progress_percentage": 40},
    )

    result = tool_fn(rules.confirm_template_input)("rule-a", "task-a", "config", "config", '{"hello":"world"}')

    assert isinstance(result, vo.ConfirmTemplateInputResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["task_name"] == "task-a"
    assert dumped["input_name"] == "config"
    assert dumped["file_url"] == "https://files.example/config.json"
    assert dumped["stored_content"] is None
    assert dumped["filename"] == "task-a_config.json"
    assert dumped["content_size"] == 17
    assert dumped["storage_type"] == "FILE"
    assert dumped["data_type"] == "FILE"
    assert dumped["format"] == "json"
    assert dumped["rule_name"] == "rule-a"
    assert dumped["rule_updated"] is True
    assert dumped["rule_status"] == "collecting_inputs"
    assert dumped["rule_progress"] == 40
    assert dumped["message"] == "Template file uploaded successfully for config in task-a. Rule 'rule-a' updated automatically."
    assert dumped["error"] is None
    assert isinstance(dumped["timestamp"], str)


def test_upload_file_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.rule, "detect_file_format", lambda file_name, content: "json")
    monkeypatch.setattr(rules.rule, "validate_and_format_content", lambda content, file_format: ('{\n  "hello": "world"\n}', True, "validated"))
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.wsutils, "post", lambda path, data, header: {"fileURL": "https://files.example/config.json"})

    result = tool_fn(rules.upload_file)("rule-a", "config.json", '{"hello":"world"}')

    assert isinstance(result, vo.UploadFileResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["file_url"] == "https://files.example/config.json"
    assert dumped["filename"] == "config.json"
    assert dumped["file_format"] == "json"
    assert dumped["validation_status"] == "validated"
    assert dumped["was_formatted"] is True
    assert dumped["message"] == "File 'config.json' uploaded successfully with JSON validation"
    assert dumped["error"] is None


def test_collect_parameter_input_returns_structured_response(monkeypatch, tool_fn):
    task = make_task(input_name="days", data_type="INT", template_content="", fmt="", default_value="7")
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(rules.rule, "validate_parameter_value", lambda value, data_type: {"valid": True, "errors": [], "converted_value": 5})

    result = tool_fn(rules.collect_parameter_input)("task-a", "days", user_value="5")

    assert isinstance(result, vo.CollectParameterInputResponseVO)
    assert result.model_dump() == {
        "success": True,
        "task_name": "task-a",
        "input_name": "days",
        "needs_default_confirmation": None,
        "default_value": None,
        "data_type": "INT",
        "required": True,
        "confirmation_message": None,
        "validated_value": 5,
        "needs_final_confirmation": True,
        "final_confirmation_message": "You entered: '5'. Is this correct? (yes/no)",
        "needs_user_input": None,
        "presentation": None,
        "has_default": None,
        "message": "Value validated - needs final confirmation before storing",
        "validation_errors": None,
        "expected_type": None,
        "error": None,
    }


def test_confirm_parameter_input_returns_structured_response(monkeypatch, tool_fn):
    task = make_task(input_name="days", data_type="INT", template_content="", fmt="", default_value="7")
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(rules.rule, "validate_parameter_value", lambda value, data_type: {"valid": True, "errors": [], "converted_value": 5})
    monkeypatch.setattr(
        rules.fetch_rule,
        "fn",
        lambda rule_name, ctx=None: {"success": True, "rule_structure": {"spec": {"inputs": {}, "inputsMeta__": []}}},
    )
    monkeypatch.setattr(
        rules.create_rule,
        "fn",
        lambda rule_structure, ctx=None: {"success": True, "detected_status": "collecting_inputs", "progress_percentage": 50},
    )

    result = tool_fn(rules.confirm_parameter_input)("task-a", "days", "days", "5", "", "final", "rule-a")

    assert isinstance(result, vo.ConfirmParameterInputResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["task_name"] == "task-a"
    assert dumped["input_name"] == "days"
    assert dumped["stored_value"] == 5
    assert dumped["data_type"] == "INT"
    assert dumped["required"] is True
    assert dumped["storage_type"] == "MEMORY"
    assert dumped["confirmation_type"] == "final"
    assert dumped["rule_name"] == "rule-a"
    assert dumped["rule_updated"] is True
    assert dumped["rule_status"] == "collecting_inputs"
    assert dumped["rule_progress"] == 50
    assert dumped["message"] == "Parameter value confirmed and stored in memory for days. Rule 'rule-a' updated automatically."
    assert dumped["validation_errors"] is None
    assert dumped["error"] is None
    assert isinstance(dumped["timestamp"], str)


def test_prepare_input_collection_overview_returns_structured_response(monkeypatch, tool_fn):
    task = make_task(input_name="config", data_type="FILE", template_content='{"hello":"world"}', fmt="json")
    monkeypatch.setattr(rules.rule, "fetch_task_api", lambda params, ctx=None: {"items": [task.to_dict()]})
    monkeypatch.setattr(rules, "validate_input_name", lambda name: name)
    monkeypatch.setattr(rules.rule, "generate_input_overview_presentation_with_validation_checkpoints", lambda analysis: "overview")

    result = tool_fn(rules.prepare_input_collection_overview)([{"task_name": "task-a", "task_alias": "step1"}])

    assert isinstance(result, vo.InputCollectionOverviewResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["overview_presentation"] == "overview"
    assert dumped["task_alias_map"] == {"step1": {"task_name": "task-a", "purpose": ""}}
    assert dumped["rule_creation_ready"] is True
    assert dumped["selected_tasks"] == [{"task_name": "task-a", "task_alias": "step1"}]
    assert dumped["validation_checkpoint_count"] == 1
    assert dumped["message"] == "Input overview prepared with task aliases and validation checkpoints. Present to user and get confirmation before proceeding."
    assert dumped["error"] is None


def test_verify_collected_inputs_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.rule, "generate_verification_presentation_with_unique_ids", lambda summary: "verification")
    collected_inputs = {
        "template_files": {
            "step1.config": {
                "task_name": "task-a",
                "filename": "config.json",
                "file_url": "https://files.example/config.json",
                "file_size": 20,
                "format": "json",
                "data_type": "FILE",
                "validated": True,
                "required": True,
            }
        },
        "parameter_values": {
            "step1.days": {
                "task_name": "task-a",
                "value": 5,
                "data_type": "INT",
                "required": True,
            }
        },
        "task_alias_map": {"step1": {"task_name": "task-a", "purpose": ""}},
    }

    result = tool_fn(rules.verify_collected_inputs)(collected_inputs)

    assert isinstance(result, vo.VerifyCollectedInputsResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["verification_presentation"] == "verification"
    assert dumped["ready_for_creation"] is True
    assert dumped["missing_count"] == 0
    assert dumped["structured_inputs"] == {"config": "https://files.example/config.json", "days": 5}
    assert dumped["task_alias_map"] == {"step1": {"task_name": "task-a", "purpose": ""}}
    assert dumped["rule_finalization_ready"] is True
    assert dumped["message"] == "Input verification prepared with task aliases. Present to user for confirmation, then automatically finalize rule."
    assert dumped["error"] is None


def test_execute_task_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.get_task_details,
        "fn",
        lambda task_name, ctx=None: {
            "inputs": [{"name": "config", "required": True}],
            "appTags": {"appType": ["nocredapp"]},
        },
    )
    monkeypatch.setattr(
        rules.rule,
        "execute_task",
        lambda request_body, ctx=None: {
            "status": "COMPLETED",
            "taskOutputs": {
                "Outputs": {
                    "report": "https://files.example/report.json",
                    "summary": "ok",
                }
            },
            "errors": [],
        },
    )

    result = tool_fn(rules.execute_task)("task-a", {"config": "value"})

    assert isinstance(result, vo.ExecuteTaskResponseVO)
    assert result.model_dump() == {
        "success": True,
        "execution_status": "COMPLETED",
        "task_name": "task-a",
        "task_inputs": {"config": "value"},
        "outputs": {"report": "https://files.example/report.json", "summary": "ok"},
        "output_files": {"report": "https://files.example/report.json"},
        "errors": None,
        "required_app_type": None,
        "input_name": None,
        "missing_inputs": None,
        "hint": "Use the outputs from this task as inputs for dependent tasks",
        "next_action": "proceed_to_next_task",
        "message": "✅ Task 'task-a' executed successfully.",
        "exception_type": None,
        "error": None,
    }


def test_fetch_execution_progress_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {
            "status": "INPROGRESS",
            "taskProgressSummary": {"progressPercentage": 40},
            "progress": [
                {
                    "taskId": "1",
                    "name": "fetch_users",
                    "type": "HTTP",
                    "status": "INPROGRESS",
                    "progressPercentage": 40,
                    "outputs": {"report": "https://files.example/report.json"},
                }
            ],
            "timestamp": "2026-03-25T10:00:00Z",
        },
    )

    result = tool_fn(rules.fetch_execution_progress)("rule-a", "exec-1")

    assert isinstance(result, vo.ExecutionProgressResponseVO)
    assert result.model_dump() == {
        "success": True,
        "continue_polling": True,
        "polling_interval_seconds": 1,
        "display_mode": "replace",
        "status": "INPROGRESS",
        "rule_name": "rule-a",
        "execution_id": "exec-1",
        "overall_progress_percentage": 40,
        "task_stats": {
            "completed": 0,
            "in_progress": 1,
            "error": 0,
            "pending": 0,
            "total": 1,
        },
        "display_lines": [
            {
                "text": "• fetch_users (HTTP) 🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜ 40% INPROGRESS",
                "task_name": "fetch_users",
                "task_type": "HTTP",
                "progress_bar": "🟩🟩🟩🟩⬜⬜⬜⬜⬜⬜",
                "percentage": 40,
                "status": "INPROGRESS",
                "outputs": {"report": "https://files.example/report.json"},
            }
        ],
        "display_header": "🔄 **Execution Progress** - rule-a",
        "display_footer": "Status: INPROGRESS | Progress: 0/1 tasks",
        "transaction_count": 1,
        "unique_task_count": 1,
        "timestamp": "2026-03-25T10:00:00Z",
        "completion_summary": None,
        "error": None,
    }


def test_fetch_output_file_returns_structured_response(monkeypatch, tool_fn, encode_json):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {
            "fileContent": encode_json({"hello": "world"}),
            "fileName": "report.json",
        },
    )
    monkeypatch.setattr(rules.rule, "get_json_preview", lambda content, size_kb: ('{\n  "hello": "world"\n}', "All 1 records shown"))

    result = tool_fn(rules.fetch_output_file)("https://files.example/report.json")

    assert isinstance(result, vo.FetchOutputFileResponseVO)
    assert result.model_dump() == {
        "success": True,
        "file_url": "https://files.example/report.json",
        "filename": "report.json",
        "file_format": "json",
        "file_size_kb": 0.02,
        "display_content": '{\n  "hello": "world"\n}',
        "user_message": "📄 JSON file (0.02KB). All 1 records shown",
        "error": None,
    }


def test_fetch_applications_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "get",
        lambda path, header: {
            "items": [
                {"meta": {"name": "GitHub App", "labels": {"appType": ["github"]}}},
                {"meta": {"name": "Jira App", "labels": {"appType": ["jira"]}}},
            ]
        },
    )

    result = tool_fn(rules.fetch_applications)()

    assert isinstance(result, vo.FetchApplicationsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "applications": [
            {"application_class_name": "GitHub App", "app_type": "github"},
            {"application_class_name": "Jira App", "app_type": "jira"},
        ],
        "message": None,
        "error": None,
    }


def test_prepare_applications_for_execution_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.fetch_rule,
        "fn",
        lambda rule_name, ctx=None: {
            "success": True,
            "rule_structure": {
                "spec": {
                    "tasks": [
                        {"name": "fetch", "alias": "step1", "appTags": {"appType": ["github"]}},
                        {"name": "sync", "alias": "step2", "appTags": {"appType": ["github"]}},
                    ]
                }
            },
        },
    )

    result = tool_fn(rules.prepare_applications_for_execution)("rule-a")

    assert isinstance(result, vo.PrepareApplicationsForExecutionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "app_type_tasks": {
            "github": [
                {
                    "task_name": "fetch",
                    "task_alias": "step1",
                    "app_tags": {"appType": ["github"]},
                    "has_unique_identifier": False,
                },
                {
                    "task_name": "sync",
                    "task_alias": "step2",
                    "app_tags": {"appType": ["github"]},
                    "has_unique_identifier": False,
                },
            ]
        },
        "tasks_needing_apps": [
            {
                "task_name": "fetch",
                "task_alias": "step1",
                "app_tags": {"appType": ["github"]},
                "has_unique_identifier": False,
            },
            {
                "task_name": "sync",
                "task_alias": "step2",
                "app_tags": {"appType": ["github"]},
                "has_unique_identifier": False,
            },
        ],
        "needs_differentiation": {
            "github": {
                "tasks": [
                    {
                        "task_name": "fetch",
                        "task_alias": "step1",
                        "app_tags": {"appType": ["github"]},
                        "has_unique_identifier": False,
                    },
                    {
                        "task_name": "sync",
                        "task_alias": "step2",
                        "app_tags": {"appType": ["github"]},
                        "has_unique_identifier": False,
                    },
                ],
                "count": 2,
                "recommendation": "Ask user if they want to use the SAME application for all tasks or DIFFERENT applications",
            }
        },
        "total_app_types": 1,
        "applications_required": True,
        "guidance": [
            "⚠️ Multiple tasks share the same application type. You need to decide:",
            "  - github: Tasks ['step1', 'step2']",
            "    Option A: Use SAME application for all (shared credentials)",
            "    Option B: Use DIFFERENT applications (requires unique identifiers)",
        ],
        "next_steps": [
            "1. For each appType with multiple tasks, ask user: 'Share same application or use different applications?'",
            "2. If DIFFERENT: Call add_unique_identifier_to_task() for each task",
            "3. Then configure applications with matching identifiers",
            "4. Call execute_rule() with the configured applications",
        ],
        "message": "Analysis complete. Found 1 application types across 2 tasks.",
        "error": None,
    }


def test_check_rule_status_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.fetch_rule,
        "fn",
        lambda rule_name, ctx=None: {
            "success": True,
            "rule_structure": {
                "meta": {"last_updated": "2026-03-25T10:00:00Z", "created_at": "2026-03-25T09:00:00Z"},
                "spec": {
                    "tasks": [{"name": "fetch"}],
                    "inputs": {"config": "https://files.example/config.json"},
                    "inputsMeta__": [{"name": "config"}],
                    "ioMap": [{"from": "a", "to": "b"}],
                    "outputsMeta__": [
                        {"name": "CompliancePCT_"},
                        {"name": "ComplianceStatus_"},
                        {"name": "LogFile"},
                    ],
                },
            },
        },
    )

    result = tool_fn(rules.check_rule_status)("rule-a")

    assert isinstance(result, vo.CheckRuleStatusResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["status_info"]["rule_name"] == "rule-a"
    assert dumped["status_info"]["inferred_status"] == "ACTIVE"
    assert dumped["status_info"]["inferred_phase"] == "completed"
    assert dumped["status_info"]["progress_percentage"] == 100
    assert dumped["status_info"]["missing_components"] == []
    assert dumped["status_info"]["next_action"] == "rule_complete"
    assert dumped["status_info"]["message"] == "✅ Rule 'rule-a' is complete and ready to use!"
    assert dumped["rule_structure_summary"] == {
        "has_tasks": True,
        "has_inputs": True,
        "has_outputs": True,
        "has_io_mapping": True,
        "total_components": 4,
        "completion_percentage": 100,
        "components_missing": 0,
        "components_complete": 4,
    }
    assert dumped["auto_inference_details"]["status_source"] == "analyzed_rule_content"
    assert dumped["auto_inference_details"]["reliable"] is True
    assert dumped["suggested_action"] is None
    assert dumped["error"] is None


def test_generate_design_notes_preview_returns_structured_response(tool_fn):
    result = tool_fn(rules.generate_design_notes_preview)("rule-a")

    assert isinstance(result, vo.DesignNotesPreviewResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "design_notes_structure": {},
        "sections_count": 7,
        "message": "MCP should construct complete notebook structure for rule 'rule-a' based on the detailed template instructions above",
        "next_action": "MCP should use fetch_rule() and build complete notebook dictionary, then return it in design_notes_structure",
        "error": None,
    }


def test_create_design_notes_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.rule, "encode_content", lambda content: "encoded")
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {"message": "Design notes file created successfully."},
    )

    result = tool_fn(rules.create_design_notes)("rule-a", {"cells": [{}, {}]})

    assert isinstance(result, vo.DesignNotesMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "filename": "rule-a.ipynb",
        "sections_saved": 2,
        "message": "Design notes successfully created and saved for rule 'rule-a'",
        "error": None,
    }


def test_fetch_rule_design_notes_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.rule, "decode_content", lambda content: {"cells": []})
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {
            "fileName": "rule-a.ipynb",
            "designNotesContent": "encoded",
        },
    )

    result = tool_fn(rules.fetch_rule_design_notes)("rule-a")

    assert isinstance(result, vo.FetchRuleDesignNotesResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "filename": "rule-a.ipynb",
        "designNotesContent": {"cells": []},
        "message": "Design notes successfully retrieved for rule rule-a. Displaying content to user.",
        "error": None,
    }


def test_generate_rule_readme_preview_returns_structured_response(tool_fn):
    result = tool_fn(rules.generate_rule_readme_preview)("rule-a")

    assert isinstance(result, vo.RuleReadmePreviewResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "readme_content": "",
        "sections_count": 12,
        "estimated_length": "2000-3000 lines",
        "message": "MCP should construct complete README.md content for rule 'rule-a' based on the detailed template instructions above",
        "next_action": "MCP should use fetch_rule() and build complete README markdown content, then return it in readme_content",
        "error": None,
    }


def test_create_rule_readme_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.rule, "encode_content", lambda content: "encoded")
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {"message": "Read-me file created successfully."},
    )

    result = tool_fn(rules.create_rule_readme)("rule-a", "## Intro\n## Usage")

    assert isinstance(result, vo.RuleReadmeMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "filename": "README.md",
        "content_length": 16,
        "sections_saved": 2,
        "message": "README.md successfully created and saved for rule 'rule-a'",
        "error": None,
    }


def test_update_rule_readme_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(rules.rule, "encode_content", lambda content: "encoded")
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {"message": "Read-me file created successfully."},
    )

    result = tool_fn(rules.update_rule_readme)("rule-a", "# Title")

    assert isinstance(result, vo.RuleReadmeMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "filename": "README.md",
        "content_length": 7,
        "sections_saved": None,
        "message": "README.md successfully updated for rule 'rule-a'",
        "error": None,
    }


def test_get_application_info_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "get",
        lambda path, params, header: {
            "items": [
                {
                    "supportedCreds": [
                        {"type": "ApiKey", "attributes": [{"name": "token", "required": True}]}
                    ]
                }
            ]
        },
    )

    result = tool_fn(rules.get_application_info)("github")

    assert isinstance(result, vo.ApplicationInfoResponseVO)
    assert result.model_dump() == {
        "success": True,
        "app_name": "github",
        "supportedCreds": [{"type": "ApiKey", "attributes": [{"name": "token", "required": True}]}],
        "message": "Retrieved information for application 'github'. User can select credential type and provide values.",
        "error": None,
    }


def test_add_unique_identifier_to_task_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.fetch_rule,
        "fn",
        lambda rule_name, ctx=None: {
            "success": True,
            "rule_structure": {
                "meta": {"labels": {"appType": ["github"]}},
                "spec": {
                    "tasks": [
                        {"name": "fetch", "alias": "step1", "appTags": {"appType": ["github"]}}
                    ]
                },
            },
        },
    )
    monkeypatch.setattr(
        rules.create_rule,
        "fn",
        lambda rule_structure, *args: {"success": True},
    )

    result = tool_fn(rules.add_unique_identifier_to_task)("rule-a", "step1", "purpose", "source")

    assert isinstance(result, vo.AddUniqueIdentifierResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "task_alias": "step1",
        "identifier_added": {"key": "purpose", "value": "source"},
        "updated_app_tags": {"appType": ["github"], "purpose": ["source"]},
        "message": "Added 'purpose': ['source'] to task 'step1'",
        "next_step": "When configuring application for this task, include 'purpose': ['source'] in appTags",
        "application_config_example": {
            "applicationType": "<application_class_name>",
            "applicationId": "<app_id> OR provide credentials",
            "appTags": {"appType": ["github"], "purpose": ["source"]},
        },
        "error": None,
    }


def test_fetch_rules_suggestions_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "fetch_rules_and_tasks_suggestions",
        lambda query, identifierType, ctx=None: [
            vo.SimplifiedRulesAndTasksSuggestionVO(
                name="GithubMergedPRApprovals",
                purpose="Validate PR approvals",
                description="Checks merged PR approvals",
            )
        ],
    )

    result = tool_fn(rules.fetch_rules_suggestions)("check github pr approvals", "Validate GitHub merged PR approvals")

    assert isinstance(result, vo.RulesSuggestionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rules": [
            {
                "name": "GithubMergedPRApprovals",
                "purpose": "Validate PR approvals",
                "description": "Checks merged PR approvals",
            }
        ],
        "message": "Found 1 suggested rules for the provided requirement.",
        "error": None,
    }


def test_get_task_details_returns_structured_response(monkeypatch, tool_fn, encode_json):
    monkeypatch.setattr(
        rules.rule,
        "fetch_task_api",
        lambda params, ctx=None: {
            "items": [
                {
                    "name": "task-a",
                    "displayName": "task-a",
                    "version": "1.0.0",
                    "description": "Task description",
                    "type": "primitive",
                    "tags": ["primitive"],
                    "applicationType": "nocredapp",
                    "inputs": [
                        {
                            "name": "config",
                            "description": "Config file",
                            "dataType": "FILE",
                            "defaultValue": "",
                            "showField": True,
                            "required": True,
                            "templateFile": encode_json({"hello": "world"}),
                            "format": "json",
                        }
                    ],
                    "outputs": [{"name": "report", "description": "Report", "dataType": "STRING"}],
                    "appTags": {"appType": ["nocredapp"]},
                    "readmeData": encode_json({"note": "sample"}),
                }
            ]
        },
    )
    monkeypatch.setattr(rules.rule, "decode_content", lambda content: "decoded readme")

    result = tool_fn(rules.get_task_details)("task-a")

    assert isinstance(result, vo.TaskDetailsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "name": "task-a",
        "description": "Task description",
        "tags": ["primitive"],
        "appTags": {"appType": ["nocredapp"]},
        "readme_content": "decoded readme",
        "inputs": [
            {
                "name": "config",
                "description": "Config file",
                "dataType": "FILE",
                "required": True,
                "has_template": True,
                "format": "json",
            }
        ],
        "outputs": [{"name": "report", "description": "Report", "dataType": "STRING"}],
        "template_count": 1,
        "message": "Use get_template_guidance('task-a', '<input_name>') for template details",
        "error": None,
    }


def test_get_rules_summary_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.rule,
        "fetch_rules_api",
        lambda ctx=None: [
            vo.SimplifiedRuleVO(
                id="rule-1",
                name="RuleOne",
                purpose="Validate policy",
                description="Checks policy compliance",
            )
        ],
    )

    result = tool_fn(rules.get_rules_summary)()

    assert isinstance(result, vo.SimplifiedRuleListVO)
    assert result.model_dump() == {
        "success": True,
        "rules": [
            {
                "id": "rule-1",
                "name": "RuleOne",
                "purpose": "Validate policy",
                "description": "Checks policy compliance",
            }
        ],
        "error": None,
    }


def test_execute_rule_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "post",
        lambda path, data, header: {"id": "exec-123", "status": "started"},
    )

    result = tool_fn(rules.execute_rule)(
        "rule-a",
        "2026-03-01",
        "2026-03-31",
        [{"name": "config", "value": "abc", "defaultValue": "abc"}],
        [],
        False,
    )

    assert isinstance(result, vo.ExecuteRuleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "execution_id": "exec-123",
        "result": {"id": "exec-123", "status": "started"},
        "message": "Rule 'rule-a' started executing.",
        "error": None,
    }


def test_configure_rule_output_schema_returns_structured_response(tool_fn):
    result = tool_fn(rules.configure_rule_output_schema)()

    assert isinstance(result, vo.RuleOutputSchemaConfigResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["user_prompt"].startswith("In ComplianceCow, evidence is stored in a structured format.")
    assert dumped["message"] == "Proceeding to user selection: Standard schema, Extended schema, or Standard + Extended."
    assert dumped["next_step"] == "Generates a JS chart (Mermaid/D3) to visualize the rule's I/O fields and task structure. The chart must be shown in this chat immediately after user input. NOTE: No further processing should occur before this step."
    assert dumped["error"] is None


def test_fetch_rule_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.wsutils, "create_header", lambda ctx=None: {})
    monkeypatch.setattr(rules.wsutils, "build_api_url", lambda endpoint: endpoint)
    monkeypatch.setattr(
        rules.wsutils,
        "get",
        lambda path, header: {
            "items": [
                {
                    "apiVersion": "v1alpha1",
                    "spec": {"ioMap": []},
                    "meta": {"name": "rule-a"},
                }
            ]
        },
    )

    result = tool_fn(rules.fetch_rule)("rule-a")

    assert isinstance(result, vo.RuleDetailsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_name": "rule-a",
        "rule_structure": {
            "apiVersion": "rule.policycow.live/v1alpha1",
            "spec": {"ioMap": []},
            "meta": {"name": "rule-a"},
        },
        "message": "Rule 'rule-a' retrieved successfully",
        "error": None,
    }


def test_create_rule_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(rules.rule, "validate_rule_structure", lambda rule_structure: {"valid": True, "errors": []})
    monkeypatch.setattr(
        rules.fetch_applications,
        "fn",
        lambda ctx=None: vo.FetchApplicationsResponseVO(
            success=True,
            applications=[{"application_class_name": "GitHub App", "app_type": "github"}],
        ),
    )
    monkeypatch.setattr(rules.rule, "generate_yaml_preview", lambda rule_structure: "yaml-preview")
    monkeypatch.setattr(
        rules.rule,
        "create_rule_api",
        lambda rule_structure, ctx=None: {
            "rule_id": "rule-123",
            "status": "created",
            "timestamp": "2026-03-25T10:00:00Z",
        },
    )
    monkeypatch.setattr(
        rules.add_rule_tag,
        "fn",
        lambda rule_name, ctx=None: {"success": True, "message": "tagged"},
    )

    rule_structure = {
        "apiVersion": "rule.policycow.live/v1alpha1",
        "kind": "rule",
        "meta": {
            "name": "rule-a",
            "purpose": "Validate GitHub policy",
            "description": "Rule description",
            "labels": {"appType": ["github"], "environment": ["logical"], "execlevel": ["app"]},
            "annotations": {"annotateType": ["github"]},
        },
        "spec": {
            "inputs": {},
            "inputsMeta__": [],
            "outputsMeta__": [],
            "tasks": [{"name": "fetch", "alias": "step1", "appTags": {"appType": ["github"]}}],
            "ioMap": [],
        },
    }

    result = tool_fn(rules.create_rule)(rule_structure, False)

    assert isinstance(result, vo.RuleCreateUpdateResponseVO)
    dumped = result.model_dump()
    assert dumped["success"] is True
    assert dumped["rule_id"] == "rule-123"
    assert dumped["rule_name"] == "rule-a"
    assert dumped["is_update"] is False
    assert dumped["detected_status"] == "DRAFT"
    assert dumped["creation_phase"] == "tasks_selected"
    assert dumped["progress_percentage"] == 25
    assert dumped["yaml_preview"] == "yaml-preview"
    assert dumped["timestamp"] == "2026-03-25T10:00:00Z"
    assert dumped["status"] == "created"
    assert dumped["tag_status"] == {"tagged": True, "message": "tagged"}
    assert dumped["next_step"] == "Call prepare_input_collection_overview() to analyze input requirements and start collection."
    assert dumped["error"] is None


def test_update_rule_returns_structured_response(monkeypatch, tool_fn):
    monkeypatch.setattr(
        rules.create_rule,
        "fn",
        lambda rule_structure, is_update, ctx=None: vo.RuleCreateUpdateResponseVO(
            success=True,
            rule_id="rule-123",
            rule_name=rule_structure["meta"]["name"],
            is_update=is_update,
            message="updated",
        ),
    )

    result = tool_fn(rules.update_rule)({"meta": {"name": "rule-a"}}, "rule-a")

    assert isinstance(result, vo.RuleCreateUpdateResponseVO)
    assert result.model_dump() == {
        "success": True,
        "rule_id": "rule-123",
        "rule_name": "rule-a",
        "is_update": True,
        "detected_status": None,
        "creation_phase": None,
        "progress_percentage": None,
        "completion_analysis": None,
        "message": "updated",
        "rule_structure": None,
        "yaml_preview": None,
        "timestamp": None,
        "status": None,
        "design_notes_info": None,
        "readme_info": None,
        "tag_status": None,
        "ui_url": None,
        "next_step": None,
        "validation_errors": None,
        "error": None,
    }
