import pytest

from constants import constants
from mcptypes import assessment_config_tool_types as vo
from tools.assessments.config import config


@pytest.mark.asyncio
async def test_list_all_assessment_categories_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_ASSESSMENT_CATEGORIES
        assert method == "GET"
        assert request_body is None
        return [
            {"id": "cat-1", "name": "Security"}
        ]

    monkeypatch.setattr(config.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(config.list_all_assessment_categories)()

    assert isinstance(result, vo.CategoryListVO)
    assert result.model_dump() == {
        "categories": [{"id": "cat-1", "name": "Security"}],
        "error": None,
    }

@pytest.mark.asyncio
async def test_list_assessments_positive(monkeypatch, tool_fn):
    captured = {}

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        captured["url"] = url
        captured["method"] = method
        captured["request_body"] = request_body
        return {
            "items": [
                {"id": "plan-1", "name": "SOC", "categoryName": "Security"},
            ]
        }

    monkeypatch.setattr(config.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(config.list_assessments)(
        categoryId="cat-1",
        categoryName="Security",
        assessmentName="SOC",
    )

    assert captured["url"] == constants.URL_PLANS
    assert captured["method"] == "GET"
    assert captured["request_body"] == {
        "fields": "basic",
        "category_id": "cat-1",
        "category_name_contains": "Security",
        "name_contains": "SOC",
    }
    assert isinstance(result, vo.AssessmentListVO)
    assert result.model_dump() == {
        "assessments": [{"id": "plan-1", "name": "SOC", "category_name": "Security"}],
        "error": None,
    }
