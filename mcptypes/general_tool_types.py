from typing import Optional

from pydantic import BaseModel
from mcptypes.error_type import StructuredError


class FileReadResultVO(BaseModel):
    content: Optional[str] = None
    uri: Optional[str] = ""
    mime_type: Optional[str] = ""
    file_size: Optional[int] = None
    file_name: Optional[str] = ""
    character_count: Optional[int] = None
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }


class DownloadableFileVO(BaseModel):
    filename: Optional[str] = ""
    url: Optional[str] = ""
    error: Optional[StructuredError] = None

    model_config = {
        "extra": "ignore",
    }
