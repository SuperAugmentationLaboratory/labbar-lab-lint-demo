# models/upload.py
from pydantic import BaseModel
from typing import List, Optional

class UploadResponse(BaseModel):
    success: bool
    files: List[str]
    message: str

class UploadError(BaseModel):
    detail: str
    error_code: str
    additional_info: Optional[dict] = None