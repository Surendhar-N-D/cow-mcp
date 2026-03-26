from typing import List, Optional

from pydantic import BaseModel
from mcptypes.error_type import StructuredError


class CategoryVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""

    model_config = {
        "extra": "ignore",
    }


class CategoryListVO(BaseModel):
    categories: Optional[List[CategoryVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }


class AssessmentVO(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    category_name: Optional[str] = ""

    model_config = {
        "extra": "ignore",
    }


class AssessmentListVO(BaseModel):
    assessments: Optional[List[AssessmentVO]] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }
