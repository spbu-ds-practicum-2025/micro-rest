from pydantic import BaseModel, Field, ConfigDict


class TaskOut(BaseModel):
    """
    Схема задачи, соответствующая components.schemas.Task из course.api.
    id, moduleId, title, description, maxScore.
    """
    id: int = Field(..., description="Идентификатор задачи (из БД)")
    moduleId: int = Field(..., description="Идентификатор модуля, к которому относится задача")
    title: str = Field(..., description="Краткое название задачи")
    description: str = Field(..., description="Полное условие задачи")
    maxScore: int = Field(..., description="Максимальное количество баллов за задачу")

    model_config = ConfigDict(from_attributes=True)
