import pytest

from constants import constants
from mcptypes import metrics_tool_types as vo
from tools.metrics import metrics


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
async def test_get_metrics_assessment_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLANS
        assert method == "GET"
        assert request_body == {"fields": "basic", "name": "Metric Manager"}
        return {
            "items": [
                {"id": "plan-1", "name": "Metric Manager", "categoryName": "Metric Manager"}
            ]
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.get_metrics_assessment)()

    assert isinstance(result, vo.MetricsAssessmentResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "id": "plan-1",
            "name": "Metric Manager",
            "category_name": "Metric Manager",
        },
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_assets_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_ASSETS
        assert method == "GET"
        return {"items": [{"id": "asset-1", "name": "EC2"}, {"id": "asset-2", "name": "S3"}]}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.list_assets)()

    assert isinstance(result, vo.MetricsAssetListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": [
            {"id": "asset-1", "name": "EC2"},
            {"id": "asset-2", "name": "S3"},
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_assets_data_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"items": [{"id": "asset-1", "name": "EC2"}]},
            {"items": [{"id": "run-1"}]},
            {
                "items": [
                    {
                        "controlId": "metric-1",
                        "name": "Public Access",
                        "description": "Checks public exposure",
                        "evidence": [
                            {"name": "Snapshot", "description": "State snapshot"},
                            {"name": "LogFile", "description": "ignored"},
                        ],
                    }
                ]
            },
        ]
    )

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return next(responses)

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.get_assets_data)("asset-1")

    assert isinstance(result, vo.AssetDataResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "assetName": "EC2",
            "assetId": "asset-1",
            "requiresNarrowing": False,
            "metrics": [
                {
                    "metricsId": "metric-1",
                    "metricsName": "Public Access",
                    "metricsDescription": "Checks public exposure",
                    "evidence": [
                        {
                            "evidenceName": "Snapshot",
                            "evidenceDescription": "State snapshot",
                        }
                    ],
                }
            ],
        },
        "next_action": None,
        "next_step": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_asset_metrics_evidence_sample_data_returns_structured_response(monkeypatch, tool_fn):
    responses = iter(
        [
            {"items": [{"id": "asset-1", "name": "EC2"}]},
            {"items": [{"id": "run-1"}]},
            {
                "items": [
                    {
                        "controlId": "metric-1",
                        "name": "Public Access",
                        "description": "Checks public exposure",
                        "evidence": [
                            {
                                "name": "Snapshot",
                                "description": "State snapshot",
                                "fileName": "snapshot.csv",
                            }
                        ],
                    }
                ]
            },
        ]
    )

    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return next(responses)

    async def fake_fetch_sample(ctx, evidence, sample_size=3, ignored_evidence_names=None, excluded_columns=None):
        assert sample_size == 3
        return {
            "evidenceRunId": "evi-1",
            "evidenceName": evidence["name"],
            "evidenceDescription": evidence["description"],
            "sampleRecords": [{"id": 1, "status": "ok"}],
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)
    monkeypatch.setattr(metrics, "fetch_evidence_sample", fake_fetch_sample)

    result = await tool_fn(metrics.get_asset_metrics_evidence_sample_data)(
        assetId="asset-1",
        metricsIds=["metric-1"],
        sampleRecordsPerEvidence=3,
    )

    assert isinstance(result, vo.AssetMetricsEvidenceSampleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "assetId": "asset-1",
            "metrics": [
                {
                    "metricsId": "metric-1",
                    "metricsName": "Public Access",
                    "metricsDescription": "Checks public exposure",
                    "evidence": [
                        {
                            "evidenceRunId": "evi-1",
                            "evidenceName": "Snapshot",
                            "evidenceDescription": "State snapshot",
                            "sampleRecords": [{"id": 1, "status": "ok"}],
                        }
                    ],
                }
            ],
        },
        "errors": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_fetch_metrics_source_summary_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_FETCH_SOURCE_SUMMARY
        assert method == "POST"
        assert payload == {"controlID": "metric-1"}
        return {
            "assessmentId": "plan-1",
            "assessmentName": "Metric Manager",
            "controlId": "metric-1",
            "controlName": "Public Access",
            "lineage": [
                {
                    "originType": "EVIDENCE",
                    "recursionLevel": 1,
                    "linkedFrom": [],
                    "evidences": [],
                    "rule": None,
                }
            ],
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.fetch_metrics_source_summary)("metric-1")

    assert isinstance(result, vo.MetricsSourceSummaryResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "assessmentMetricsId": "plan-1",
            "assessmentMetricsName": "Metric Manager",
            "metricsId": "metric-1",
            "metricsName": "Public Access",
            "lineage": [
                {
                    "originType": "EVIDENCE",
                    "recursionLevel": 1,
                    "linkedFrom": [],
                    "evidences": [],
                    "rule": None,
                }
            ],
        },
        "error": None,
        "next_action": "get evidence sample data",
        "next_step": None,
    }


@pytest.mark.asyncio
async def test_run_metrics_assessment_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_INSTANCES
        assert method == "POST"
        return {"id": "run-1", "status": "queued", "name": "Daily Run", "description": "Daily metrics"}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.run_metrics_assessment)("plan-1", "Daily Run", "Daily metrics")

    assert isinstance(result, vo.MetricsRunResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "runId": "run-1",
            "status": "queued",
            "name": "Daily Run",
            "description": "Daily metrics",
        },
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_all_recent_assessment_run_details_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_INSTANCES
        assert method == "GET"
        assert request_body["plan_id"] == "plan-1"
        return {"items": [{"id": "run-1", "name": "Daily Run", "started": "2026-03-25T10:00:00Z", "status": "completed"}]}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.get_all_recent_assessment_run_details)("plan-1")

    assert isinstance(result, vo.RecentMetricsRunListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": [
            {
                "metricAssessmentRunId": "run-1",
                "name": "Daily Run",
                "runTime": "2026-03-25T10:00:00Z",
                "status": "completed",
            }
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_all_metrics_of_run_returns_structured_response(monkeypatch, tool_fn):
    async def fake_controls(ctx, assessment_run_id, basicFields=False):
        assert assessment_run_id == "run-1"
        return (
            {
                "items": [
                    {
                        "id": "metric-run-1",
                        "name": "Public Access",
                        "description": "Checks exposure",
                        "controlId": "metric-1",
                        "displayable": "1.1",
                        "evidences": [
                            {
                                "name": "DerivedEvidence",
                                "status": "completed",
                                "compliancePCT__": 88,
                                "ruleId": "rule-1",
                                "complianceCalculationInfos": {"gocel": {"include": "a > 0", "compliance": "b == 1"}},
                            },
                            {"name": "AuditFile", "status": "completed"},
                        ],
                    }
                ]
            },
            None,
        )

    monkeypatch.setattr(metrics, "get_assessment_run_controls", fake_controls)

    result = await tool_fn(metrics.get_all_metrics_of_run)("run-1", "plan-1")

    assert isinstance(result, vo.MetricsRunDetailsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {
            "assessmentMetricsRunId": "run-1",
            "assessmentMetricsId": "plan-1",
            "metrics": [
                {
                    "metricRunId": "metric-run-1",
                    "name": "Public Access",
                    "description": "Checks exposure",
                    "metricId": "metric-1",
                    "metricNumber": "1.1",
                    "formula": "(a/b)*100",
                    "metricEvidences": [
                        {
                            "name": "DerivedEvidence",
                            "status": "completed",
                            "metricScore": 88,
                            "cel_formula": {
                                "filteringExpression": "a > 0",
                                "compliantExpression": "b == 1",
                            },
                            "message": None,
                        }
                    ],
                    "metricEvidencesSources": [
                        {"name": "AuditFile", "status": "completed"}
                    ],
                }
            ],
        },
        "error": None,
    }


@pytest.mark.asyncio
async def test_add_metric_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLANS}/plan-1/add-control"
        assert method == "POST"
        return {"id": "metric-1"}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.add_metric)("plan-1", "Security", "Public access must be disabled")

    assert isinstance(result, vo.MetricCreateResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": {"metricsId": "metric-1"},
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_metric_returns_structured_response(monkeypatch, tool_fn):
    async def fake_patch(url, method, payload, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/metric-1"
        assert method == "PATCH"
        return {}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_patch)

    result = await tool_fn(metrics.update_metric)("plan-1", "metric-1", "Updated description")

    assert isinstance(result, vo.MetricUpdateResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Metrics updated successfully",
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_all_metrics_categories_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return {"items": [{"id": "cat-1", "name": "Security"}], "TotalPage": 1}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.get_all_metrics_categories)("plan-1")

    assert isinstance(result, vo.MetricsCategoryListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "data": ["Security"],
        "message": None,
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_all_assessment_metrics_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        return {
            "items": [
                {
                    "id": "metric-1",
                    "name": "Public Access",
                    "description": "Checks exposure",
                    "alias": "PUB-1",
                    "displayable": "1.1",
                }
            ],
            "TotalPage": 1,
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.get_all_assessment_metrics)("plan-1")

    assert isinstance(result, vo.AssessmentMetricsListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "metrics": [
            {
                "id": "metric-1",
                "name": "Public Access",
                "description": "Checks exposure",
                "alias": "PUB-1",
                "metricNumber": "1.1",
            }
        ],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_suggest_metrics_citations_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_GET_SIMILAR_CONTROLS
        assert method == "POST"
        return {
            "authorityDocument": "CIS",
            "items": [
                {
                    "inputMetricName": "Public Access",
                    "metricsId": "metric-1",
                    "suggestions": [
                        {
                            "Name": "CIS 1.1",
                            "Metric ID": "2001",
                            "Metric Classification": "Preventive",
                            "Impact Zone": "Storage",
                            "Metric Requirement": "Disable public access",
                            "Sort ID": "1.1",
                            "Metric Type": "Config",
                            "Score": 0.95,
                        }
                    ],
                }
            ],
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.suggest_metrics_citations)("Public Access", "plan-1", "Disable access")

    assert isinstance(result, vo.MetricCitationSuggestionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "items": [
            {
                "inputMetricName": "Public Access",
                "metricsId": "metric-1",
                "suggestions": [
                    {
                        "Name": "CIS 1.1",
                        "metric_id": "2001",
                        "metric_classification": "Preventive",
                        "impact_zone": "Storage",
                        "metric_requirement": "Disable public access",
                        "sort_id": "1.1",
                        "metric_type": "Config",
                        "score": 0.95,
                    }
                ],
            }
        ],
        "authorityDocument": "CIS",
        "error": None,
    }


@pytest.mark.asyncio
async def test_attach_citation_to_metrics_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        if url == constants.URL_PLAN_CONTROL_CITATIONS_BATCH:
            return {
                "items": [
                    {
                        "id": "cit-1",
                        "planControlID": "metric-1",
                        "authorityDocument": "CIS",
                        "controlNames": ["Public Access"],
                        "controlsInAuthorityDocument": ["2001"],
                        "sortID": "1.1",
                        "status": "active",
                    }
                ]
            }
        assert url == constants.URL_PLANS_SYNC_CCFID
        return {}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.attach_citation_to_metrics)(
        assessmentMetricsId="plan-1",
        metricsId="metric-1",
        authorityDocument="CIS",
        metricsIdsInAuthorityDocument=["2001"],
        sortId="1.1",
        metricsNames=["Public Access"],
    )

    assert isinstance(result, vo.MetricCitationAttachmentResponseVO)
    assert result.model_dump() == {
        "success": True,
        "citations": [
            {
                "id": "cit-1",
                "metricsID": "metric-1",
                "authorityDocument": "CIS",
                "metricsNames": ["Public Access"],
                "metricsIdsInAuthorityDocument": ["2001"],
                "sortID": "1.1",
                "status": "active",
            }
        ],
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_metrics_evidence_sample_data_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_FETCH_SAMPLE_EVIDENCE_DATA
        assert method == "POST"
        assert payload == {"controlID": "metric-1", "records": 2, "evidenceNames": ["EvidenceA"]}
        return [{"controlId": "metric-1", "name": "EvidenceA", "sampleRecords": [{"id": 1}]}]

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.get_metrics_evidence_sample_data)(
        metricsId="metric-1",
        evidenceNames=["EvidenceA"],
        records=2,
    )

    assert isinstance(result, vo.MetricsEvidenceSampleResponseVO)
    assert result.model_dump() == {
        "success": True,
        "metricsId": "metric-1",
        "evidences": [{"metricsId": "metric-1", "name": "EvidenceA", "sampleRecords": [{"id": 1}]}],
        "error": None,
    }


@pytest.mark.asyncio
async def test_validate_sql_query_and_cel_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_PLAN_CONTROLS_VALIDATE_SQL_QUERY
        assert method == "POST"
        assert payload["sqlQuery"] == "select * from EvidenceA"
        return {"queryStatus": "success", "data": {"columns": ["id"], "rows": [[1]]}}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.validate_sql_query_and_cel)(
        sqlQuery="select * from EvidenceA",
        referenceEvidences=[{"name": "EvidenceA", "id": "run-evi-1"}],
        assessmentMetricsId="plan-1",
        metricsId="metric-1",
        filteringCELExpression="id > 0",
        compliantCELExpression="id == 1",
    )

    assert isinstance(result, vo.MetricsSqlValidationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "resp": {"queryStatus": "success", "data": {"columns": ["id"], "rows": [[1]]}},
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_sql_query_evidence_returns_preview_response(monkeypatch, tool_fn):
    result = await tool_fn(metrics.create_sql_query_evidence)(
        metricsId="metric-1",
        sqlquery="select * from EvidenceA",
        referedEvidenceNames=["EvidenceA"],
        newEvidenceName="DerivedEvidence",
        confirm=False,
    )

    assert isinstance(result, vo.MetricSqlQueryEvidenceMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before creating SQL query",
        "controlConfigId": "metric-1",
        "evidenceId": None,
        "sqlQuery": "select * from EvidenceA",
        "newEvidenceName": "DerivedEvidence",
        "referedEvidenceNames": ["EvidenceA"],
        "next_step": "Review the SQL query above. If you need to modify it, provide the updated sqlquery parameter when calling with confirm=True. If correct, re-run with confirm=True to create and attach the query.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_sql_query_evidence_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == f"{constants.URL_PLAN_CONTROLS}/metric-1/sql-query-evidences"
        assert method == "GET"
        return {
            "items": [
                {
                    "id": "sql-evi-1",
                    "evidenceId": "evi-1",
                    "ruleId": "rule-1",
                    "sqlQuery": "select * from EvidenceA",
                    "evidenceName": "DerivedEvidence",
                    "referedEvidenceNames": ["EvidenceA"],
                }
            ]
        }

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.list_sql_query_evidence)("metric-1")

    assert isinstance(result, vo.MetricSqlQueryEvidenceListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "evidences": [
            {
                "id": "sql-evi-1",
                "evidenceId": "evi-1",
                "ruleId": "rule-1",
                "sqlQuery": "select * from EvidenceA",
                "evidenceName": "DerivedEvidence",
                "referedEvidenceNames": ["EvidenceA"],
            }
        ],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_sql_query_evidence_returns_preview_response(tool_fn):
    result = await tool_fn(metrics.update_sql_query_evidence)(
        metricsId="metric-1",
        evidenceId="evi-1",
        sqlquery="select * from EvidenceA",
        referedEvidenceNames=["EvidenceA"],
        newEvidenceName="DerivedEvidence",
        confirm=False,
    )

    assert isinstance(result, vo.MetricSqlQueryEvidenceMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before updating SQL query evidence",
        "controlConfigId": "metric-1",
        "evidenceId": "evi-1",
        "sqlQuery": "select * from EvidenceA",
        "newEvidenceName": "DerivedEvidence",
        "referedEvidenceNames": ["EvidenceA"],
        "next_step": "Review the updated SQL query above. If you need to modify it, provide the updated sqlquery parameter when calling with confirm=True. If correct, re-run with confirm=True to update the SQL query evidence.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_add_cel_expression_to_metrics_returns_structured_response(monkeypatch, tool_fn):
    async def fake_patch(url, method, payload, return_raw=False, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/metric-1/evidences/evi-1"
        assert method == "PATCH"
        assert return_raw is True
        assert payload == [
            {
                "op": "add",
                "path": "/complianceCalculationInfos",
                "value": {"gocel": {"include": "id > 0", "compliance": "id == 1"}},
            }
        ]
        return DummyRawResponse(204)

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_patch)

    result = await tool_fn(metrics.add_cel_expression_to_metrics)(
        metricsId="metric-1",
        metricsEvidenceId="evi-1",
        filteringExpression="id > 0",
        compliantExpression="id == 1",
    )

    assert isinstance(result, vo.CelMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "CEL expressions added successfully",
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_cel_expression_to_metrics_returns_structured_response(monkeypatch, tool_fn):
    async def fake_patch(url, method, payload, return_raw=False, ctx=None, **kwargs):
        assert url == f"{constants.URL_PLAN_CONTROLS}/metric-1/evidences/evi-1"
        assert method == "PATCH"
        assert return_raw is True
        return DummyRawResponse(204)

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_patch)

    result = await tool_fn(metrics.update_cel_expression_to_metrics)(
        metricsId="metric-1",
        metricsEvidenceId="evi-1",
        filteringExpression="id > 0",
        compliantExpression="id == 1",
    )

    assert isinstance(result, vo.CelMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "CEL expressions uplodated successfully",
        "error": None,
    }


@pytest.mark.asyncio
async def test_get_cel_expression_for_metrics_returns_structured_response(monkeypatch, tool_fn):
    async def fake_get_assessment_control(metrics_id, ctx=None):
        assert metrics_id == "metric-1"
        return (
            {
                "evidences": [
                    {
                        "id": "evi-1",
                        "complianceCalculationInfos": {
                            "gocel": {"include": "id > 0", "compliance": "id == 1"}
                        },
                    }
                ]
            },
            None,
        )

    monkeypatch.setattr(metrics, "get_assessment_control", fake_get_assessment_control)

    result = await tool_fn(metrics.get_cel_expression_for_metrics)("metric-1", "evi-1")

    assert isinstance(result, vo.CelExpressionResponseVO)
    assert result.model_dump() == {
        "success": True,
        "filteringExpression": "id > 0",
        "compliantExpression": "id == 1",
        "error": None,
    }


@pytest.mark.asyncio
async def test_create_metrics_note_returns_preview_response(tool_fn):
    result = await tool_fn(metrics.create_metrics_note)(
        metricsId="metric-1",
        assessmentMetricsId="plan-1",
        notes="Metric note",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.MetricNoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before creating note",
        "metricsId": "metric-1",
        "noteId": None,
        "topic": "Documentation",
        "notes": "Metric note",
        "next_step": "Review the Note above. If you need to modify it, provide the updated note parameter when calling with confirm=True. If correct, re-run with confirm=True to create note.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_list_metrics_notes_returns_structured_response(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == constants.URL_PLAN_CONTROL_NOTES.format(controlConfigId="metric-1")
        assert method == "GET"
        return {"items": [{"id": "note-1", "topic": "Documentation", "notes": "Metric note"}]}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(metrics.list_metrics_notes)("metric-1")

    assert isinstance(result, vo.MetricNoteListResponseVO)
    assert result.model_dump() == {
        "success": True,
        "notes": [{"id": "note-1", "topic": "Documentation", "notes": "Metric note"}],
        "totalCount": 1,
        "error": None,
    }


@pytest.mark.asyncio
async def test_update_metrics_note_returns_preview_response(tool_fn):
    result = await tool_fn(metrics.update_metrics_note)(
        metricsId="metric-1",
        noteId="note-1",
        assessmentId="plan-1",
        notes="Updated metric note",
        topic="Documentation",
        confirm=False,
    )

    assert isinstance(result, vo.MetricNoteMutationResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Confirmation required before updating note",
        "metricsId": "metric-1",
        "noteId": "note-1",
        "topic": "Documentation",
        "notes": "Updated metric note",
        "next_step": "Review the updated Note above. If you need to modify it, provide the updated notes or topic parameters when calling with confirm=True. If correct, re-run with confirm=True to update the note.",
        "error": None,
    }


@pytest.mark.asyncio
async def test_link_source_metrics_to_target_metric_returns_structured_response(monkeypatch, tool_fn):
    async def fake_post(url, method, payload, ctx=None, **kwargs):
        assert url == constants.URL_LINK_CONTROL
        assert method == "POST"
        assert payload == [
            {
                "sourcePlan": {"controlId": "metric-1"},
                "targetPlan": {"controlId": "metric-2"},
                "userGenerated": True,
                "propagate": "evidence",
                "propagateToSource": "none",
            }
        ]
        return {}

    monkeypatch.setattr(metrics.utils, "make_API_call_to_CCow_and_get_response", fake_post)

    result = await tool_fn(metrics.link_source_metrics_to_target_metric)(["metric-1"], "metric-2")

    assert isinstance(result, vo.LinkMetricsResponseVO)
    assert result.model_dump() == {
        "success": True,
        "message": "Source metrics were successfully linked to the target metric.",
        "error": None,
    }
