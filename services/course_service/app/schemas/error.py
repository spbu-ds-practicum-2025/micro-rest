from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ErrorResponse(BaseModel):
    """
    Общая схема ошибки, соответствующая components.schemas.ErrorResponse.
    """
    errorId: UUID = Field(..., description="Уникальный идентификатор ошибки для трассировки")
    code: Optional[str] = Field(None, description="Машиночитаемый код ошибки")
    message: str = Field(..., description="Краткое человекочитаемое описание ошибки")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Дополнительные сведения об ошибке",
    )

    model_config = ConfigDict(from_attributes=True)
