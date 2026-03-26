import pytest

from mcptypes import general_tool_types as vo
from tools.general import general


def test_read_file_positive(tmp_path, tool_fn):
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("hello world", encoding="utf-8")

    result = tool_fn(general.read_file)(str(sample_file))

    assert isinstance(result, vo.FileReadResultVO)
    assert result.model_dump() == {
        "content": "hello world",
        "uri": str(sample_file),
        "mime_type": "text/plain",
        "file_size": 11,
        "file_name": "sample.txt",
        "character_count": 11,
        "error": None,
    }


def test_read_resource_positive(tmp_path, tool_fn):
    sample_file = tmp_path / "resource.md"
    sample_file.write_text("# title", encoding="utf-8")

    result = tool_fn(general.read_resource)(str(sample_file))

    assert isinstance(result, vo.FileReadResultVO)
    assert result.model_dump()["file_name"] == "resource.md"
    assert result.model_dump()["content"] == "# title"


@pytest.mark.asyncio
async def test_create_downloadable_file_positive(monkeypatch, tool_fn):
    if not hasattr(general, "create_downloadable_file"):
        pytest.skip("create_downloadable_file is disabled in this environment")

    async def fake_upload(url, method, request_body=None, type="json", return_raw=False, ctx=None):
        assert url == "/v1/mcp-upload"
        assert method == "POST"
        assert request_body["FileType"] == ".txt"
        return "0123456789abcdef0123456789abcdef01234567"

    monkeypatch.setattr(general.utils, "make_API_call_to_CCow_and_get_response", fake_upload)

    result = await tool_fn(general.create_downloadable_file)("report.txt", "hello")

    assert isinstance(result, vo.DownloadableFileVO)
    assert result.model_dump()["filename"] == "report.txt"
    assert result.model_dump()["url"].endswith(".txt")
