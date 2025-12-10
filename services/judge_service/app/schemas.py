from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class SubmissionStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class SubmissionCreateRequest(BaseModel):
    code: str = Field(..., description="Исходный код решения")
    language: str = Field(
        ...,
        description="Язык программирования решения (например, python)",
    )


class Submission(BaseModel):
    # В спецификации format: uuid, но мы не навязываем тип UUID,
    # чтобы можно было спокойно возвращать строки.
    id: str
    taskId: str
    status: SubmissionStatus
    score: Optional[int] = None
    language: str
    createdAt: datetime
    updatedAt: Optional[datetime] = None


class ErrorResponse(BaseModel):
    errorId: str
    code: Optional[str] = None
    message: str
    details: Optional[Dict[str, Any]] = None
