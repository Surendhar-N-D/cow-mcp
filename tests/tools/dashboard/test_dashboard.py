import pytest

from constants import constants
from mcptypes import dashboard_tools_type as vo
from tools.dashboard import dashboard


@pytest.mark.asyncio
async def test_get_dashboard_review_periods_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {}
        assert url == constants.URL_CCF_DASHBOARD_REVIEW_PERIODS
        assert method == "POST"
        return {"items": ["Q1 2024", "Q2 2024"]}

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(dashboard.get_dashboard_review_periods)()

    assert isinstance(result, vo.CCFDashboardReviewPeriods)
    assert result.model_dump()["items"] == ["Q1 2024", "Q2 2024"]


@pytest.mark.asyncio
async def test_get_dashboard_data_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "ccfPeriod": "Q1 2024",
            "includeCompliancePerformance": True,
            "includeControlSummary": True,
            "includeFrameworkCompliance": True,
        }
        assert url == constants.URL_CCF_DASHBOARD_FRAMEWORK_SUMMARY
        assert method == "POST"
        return {
            "totalControls": 10,
            "controlStatus": [{"status": "Completed", "count": 6}],
            "controlAssignmentStatus": [{"categoryName": "IAM", "controlStatus": [{"status": "Completed", "count": 6}]}],
            "compliancePCT": 60.0,
            "controlSummary": [{"category": "IAM", "status": "Completed", "dueDate": "", "compliancePCT": 60.0, "leafControls": 2}],
            "complianceStatusSummary": [{"status": "COMPLIANT", "count": 6}],
            "frameworks": [{"name": "SOC 2", "compliancePCT": 60.0, "leafControls": 2, "complianceStatusSummary": [{"status": "COMPLIANT", "count": 6}]}],
        }

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(dashboard.get_dashboard_data)("Q1 2024")

    assert isinstance(result, vo.DashboardSummaryVO)
    assert result.model_dump()["totalControls"] == 10


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "function_name",
    ["fetch_dashboard_framework_controls", "fetch_dashboard_framework_summary"],
)
async def test_dashboard_framework_tools_positive(monkeypatch, tool_fn, function_name):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "ccfPeriod": "Q1 2024",
            "includeOverDueControls": False,
            "includeNonCompliantControls": False,
            "fetchleafControls": True,
            "authorityDocumentName": "SOC 2",
        }
        assert url == constants.URL_CCF_DASHBOARD_CONTROL_DETAILS
        assert method == "POST"
        return {
            "items": [{"id": "ctrl-1", "controlName": "Access Review", "status": "Completed", "complianceStatus": "COMPLIANT"}],
            "TotalItems": 1,
            "TotalPage": 1,
            "Page": 1,
        }

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(getattr(dashboard, function_name))("Q1 2024", "SOC 2")

    assert isinstance(result, vo.FrameworkControlListVO)
    assert result.model_dump()["controls"][0]["name"] == "Access Review"


@pytest.mark.asyncio
async def test_get_dashboard_common_controls_details_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "ccfPeriod": "Q1 2024",
            "includeOverDueControls": False,
            "includeNonCompliantControls": False,
            "fetchleafControls": True,
            "status": "",
            "complianceStatus": "",
            "controlCategoryName": "",
            "priority": "",
            "page": 1,
            "pageSize": 50,
        }
        assert url == constants.URL_CCF_DASHBOARD_CONTROL_DETAILS
        assert method == "POST"
        return {
            "items": [{"id": "ctrl-1", "controlName": "Access Review", "priority": "High", "status": "Completed", "complianceStatus": "COMPLIANT"}],
            "TotalItems": 1,
            "TotalPage": 1,
            "Page": 1,
        }

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(dashboard.get_dashboard_common_controls_details)("Q1 2024")

    assert isinstance(result, vo.CommonControlListVO)
    assert result.model_dump()["controls"][0]["controlName"] == "Access Review"


@pytest.mark.asyncio
async def test_get_top_over_due_controls_detail_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "ccfPeriod": "Q1 2024",
            "includeOverDueControls": True,
            "page": 1,
            "pageSize": 10,
        }
        assert url == constants.URL_CCF_DASHBOARD_CONTROL_DETAILS
        assert method == "POST"
        return {
            "items": [{"id": "ctrl-1", "controlName": "Late Control", "dueDate": "2026-03-01", "daysOverDue": 5}],
        }

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(dashboard.get_top_over_due_controls_detail)("Q1 2024", 10)

    assert isinstance(result, vo.OverdueControlListVO)
    assert result.model_dump()["controls"][0]["name"] == "Late Control"


@pytest.mark.asyncio
async def test_get_top_non_compliant_controls_detail_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {
            "ccfPeriod": "Q1 2024",
            "includeNonCompliantControls": True,
            "page": 1,
            "pageSize": 1,
        }
        assert url == constants.URL_CCF_DASHBOARD_CONTROL_DETAILS
        assert method == "POST"
        return {
            "items": [{"controlName": "Weak Control", "score": 20.0, "priority": "High"}],
        }

    monkeypatch.setattr(dashboard.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(dashboard.get_top_non_compliant_controls_detail)("Q1 2024", 1, 1)

    assert isinstance(result, vo.NonCompliantControlListVO)
    assert result.model_dump()["controls"][0]["name"] == "Weak Control"
