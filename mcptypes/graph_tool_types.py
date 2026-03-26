from typing import Any, Optional

from pydantic import BaseModel
from mcptypes.error_type import StructuredError


class UniqueNodeDataVO(BaseModel):
    node_names: Optional[list[str]] = None
    unique_property_values: Optional[list[Any]] = None
    neo4j_schema: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }


class CypherQueryVO(BaseModel):
    result: Optional[Any] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }
