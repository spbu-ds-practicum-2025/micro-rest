from pydantic import BaseModel, Field, ConfigDict


class ModuleOut(BaseModel):
    """
    Схема модуля, соответствующая components.schemas.Module из course.api.
    id, title, description, order, isRead.
    """
    id: int = Field(..., description="Идентификатор модуля (из БД)")
    title: str = Field(..., description="Название модуля")
    description: str = Field(..., description="Краткое описание содержимого модуля")
    order: int = Field(..., description="Порядковый номер модуля в курсе")
    isRead: bool = Field(..., description="Признак того, что модуль прочитан пользователем")
    content: str = Field(..., description="content itself")

    model_config = ConfigDict(from_attributes=True)
