import pytest

from constants import constants
from mcptypes import assets_tools_type as vo
from tools.assets import assets


@pytest.mark.asyncio
async def test_list_assets_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_ASSETS
        assert method == "GET"
        return {"items": [{"id": "asset-1", "name": "AWS"}]}

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.list_assets)()

    assert isinstance(result, vo.AssetListVO)
    assert result.model_dump()["assets"][0]["name"] == "AWS"


@pytest.mark.asyncio
async def test_fetch_assets_summary_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"planID": "plan-1"}
        assert url == constants.URL_FETCH_ASSETS_SUMMARY
        assert method == "POST"
        return {
            "planRunID": "run-1",
            "assessmentName": "AWS Inventory",
            "status": "Completed",
            "numberOfResources": 12,
            "numberOfChecks": {"COMPLIANT": 9, "NON_COMPLIANT": 3},
            "dataStatus": "READY",
            "createdAt": "2026-03-24T10:00:00Z",
        }

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.fetch_assets_summary)("plan-1")

    assert isinstance(result, vo.AssestsSummaryVO)
    assert result.model_dump()["integrationRunId"] == "run-1"


@pytest.mark.asyncio
async def test_fetch_resource_types_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"planRunID": "run-1", "page": 1, "pageSize": 10}
        assert url == constants.URL_FETCH_RESOURCE_TYPES
        assert method == "POST"
        return {"items": [{"resourceType": "EC2", "totalResources": 4}]}

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.fetch_resource_types)("run-1", page=1, pageSize=0)

    assert isinstance(result, vo.ResourceTypeListVO)
    assert result.model_dump()["resourceTypes"][0]["resourceType"] == "EC2"


@pytest.mark.asyncio
async def test_fetch_checks_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "planRunID": "run-1",
            "resourceType": "EC2",
            "page": 1,
            "pageSize": 10,
            "complianceStatus": "NON_COMPLIANT",
        }
        assert url == constants.URL_FETCH_CHECKS
        assert method == "POST"
        return {
            "items": [
                {
                    "name": "Encryption enabled",
                    "description": "Checks encryption",
                    "rule": {"type": "sql", "name": "check_rule"},
                    "activationStatus": "ACTIVE",
                    "priority": "HIGH",
                    "complianceStatus": "NON_COMPLIANT",
                    "compliancePCT": 25.0,
                }
            ],
            "totalItems": 1,
            "totalPage": 1,
            "page": 1,
        }

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.fetch_checks)("run-1", "EC2", page=1, pageSize=10, complianceStatus="NON_COMPLIANT")

    assert isinstance(result, vo.ChecksListVO)
    assert result.model_dump()["checks"][0]["name"] == "Encryption enabled"


@pytest.mark.asyncio
async def test_fetch_resources_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "planRunID": "run-1",
            "resourceType": "EC2",
            "page": 1,
            "pageSize": 10,
            "complianceStatus": "",
        }
        assert url == constants.URL_FETCH_RESOURCES
        assert method == "POST"
        return {
            "items": [
                {
                    "name": "i-123",
                    "resourceType": "EC2",
                    "complianceStatus": "NON_COMPLIANT",
                    "checks": [
                        {
                            "name": "Public access",
                            "description": "Detects exposure",
                            "resourceComplianceStatus": "NON_COMPLIANT",
                            "controlName": "AC-1",
                            "rule": {"type": "sql", "name": "public_access"},
                            "activationStatus": "ACTIVE",
                            "priority": "HIGH",
                        }
                    ],
                }
            ],
            "totalItems": 1,
            "totalPage": 1,
            "page": 1,
        }

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.fetch_resources)("run-1", "EC2", page=1, pageSize=10)

    assert isinstance(result, vo.ResourceListVO)
    assert result.model_dump()["resources"][0]["checks"][0]["controlName"] == "AC-1"


@pytest.mark.asyncio
async def test_fetch_resources_by_check_name_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"planRunID": "run-1", "checkName": "Public access", "page": 1, "pageSize": 10}
        assert method == "POST"
        return {
            "items": [
                {
                    "name": "i-123",
                    "resourceType": "EC2",
                    "complianceStatus": "NON_COMPLIANT",
                    "checks": [{"name": "should-be-removed"}],
                }
            ],
            "totalItems": 1,
            "totalPage": 1,
            "page": 1,
        }

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(assets.fetch_resources_by_check_name)("run-1", "Public access", page=1, pageSize=10)

    assert isinstance(result, vo.ResourceListVO)
    assert result.model_dump()["resources"][0]["checks"] is None


@pytest.mark.asyncio
async def test_fetch_resource_types_summary_positive(monkeypatch):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return {
            "items": [{"resourceType": f"type-{request_body['page']}", "totalResources": request_body["page"]}],
            "totalItems": 3,
        }

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await assets.fetch_resource_types_summary("run-1")

    assert isinstance(result, vo.ResourceTypeSummaryVO)
    assert len(result.model_dump()["resourcesTypes"]) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("function_name", "payload", "resource_type", "check"),
    [
        ("fetch_checks_summary", {"planRunID": "run-1", "resourceType": "EC2", "summaryType": "checks"}, "EC2", None),
        ("fetch_resources_summary", {"planRunID": "run-1", "resourceType": "EC2", "summaryType": "resources"}, "EC2", None),
        (
            "fetch_resources_by_check_name_summary",
            {"planRunID": "run-1", "resourceType": "EC2", "checkName": "Public access", "summaryType": "resources"},
            "EC2",
            "Public access",
        ),
    ],
)
async def test_asset_summary_tools_positive(monkeypatch, tool_fn, function_name, payload, resource_type, check):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == payload
        assert url == constants.URL_FETCH_ASSETS_DETAIL_SUMMARY
        assert method == "POST"
        return {"complianceSummary": {"COMPLIANT": 3, "NON_COMPLIANT": 1}}

    monkeypatch.setattr(assets.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    function = tool_fn(getattr(assets, function_name))
    if check is None:
        result = await function("run-1", resource_type)
    else:
        result = await function("run-1", resource_type, check)

    assert isinstance(result, (vo.CheckSummaryVO, vo.ResourceSummaryVO))
    assert result.model_dump()["complianceSummary"]["COMPLIANT"] == 3
