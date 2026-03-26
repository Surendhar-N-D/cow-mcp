import pytest

from constants import constants
from mcptypes import graph_tool_types as vo
from tools.graphdb import graphdb


@pytest.mark.asyncio
async def test_fetch_unique_node_data_and_schema_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"user_question": "show access controls"}
        assert url == constants.URL_RETRIEVE_UNIQUE_NODE_DATA_AND_SCHEMA
        assert method == "POST"

        return {
            "node_names": ["Control", "Repository"],
            "unique_property_values": [
                {
                    "node_type": "Control",
                    "property_name": "compliance_status",
                    "is_enum": True,
                    "available_options": ["A", "B"],
                },
                {
                    "node_type": "Repository",
                    "property_name": "name",
                    "is_enum": False,
                    "available_options": ["repo1", "repo2"],
                },
            ],
            "neo4j_schema": "(:Control)-[:HAS_CHILD]->(:Control)",
        }

    monkeypatch.setattr(graphdb.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(graphdb.fetch_unique_node_data_and_schema)("show access controls")

    assert isinstance(result, vo.UniqueNodeDataVO)

    data = result.model_dump()

    assert data["node_names"] == ["Control", "Repository"]
    assert data["unique_property_values"][0]["node_type"] == "Control"
    assert data["neo4j_schema"] == "(:Control)-[:HAS_CHILD]->(:Control)"


@pytest.mark.asyncio
async def test_execute_cypher_query_positive(monkeypatch, tool_fn):
    async def fake_request(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert request_body == {"query": "MATCH (n) RETURN n LIMIT 1"}
        assert url == constants.URL_EXECUTE_CYPHER_QUERY
        assert method == "POST"

        return {
            "result": {
                "control_name": ["Sample Control", "Another Control"],
                "compliance_status": ["COMPLIANT", "NON_COMPLIANT"],
                "priority": ["High", "Low"],
                "status": ["Assigned", "Unassigned"],
                "alias": ["1.1", "2.1"],
            }
        }

    monkeypatch.setattr(graphdb.utils, "make_API_call_to_CCow_and_get_response", fake_request)

    result = await tool_fn(graphdb.execute_cypher_query)("MATCH (n) RETURN n LIMIT 1")

    assert isinstance(result, vo.CypherQueryVO)

    data = result.model_dump()

    assert "result" in data
    assert data["result"]["control_name"][0] == "Sample Control"
    assert data["result"]["priority"][1] == "Low"
