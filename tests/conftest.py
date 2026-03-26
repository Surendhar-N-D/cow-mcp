import base64
import json
import sys
from dataclasses import asdict, is_dataclass
from pathlib import Path

import pytest
from pydantic import BaseModel


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def to_plain_data(value):
    if isinstance(value, BaseModel):
        return value.model_dump()
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, list):
        return [to_plain_data(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain_data(item) for key, item in value.items()}
    return value


@pytest.fixture
def serialize():
    return to_plain_data


@pytest.fixture
def tool_fn():
    def _tool_fn(tool):
        return getattr(tool, "fn", tool)

    return _tool_fn


@pytest.fixture
def encode_json():
    def _encode(payload):
        raw = json.dumps(payload).encode("utf-8")
        return base64.b64encode(raw).decode("utf-8")

    return _encode
