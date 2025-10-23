from pydantic import BaseModel
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    module_id: int
    status: Optional[str] = "todo"


class TaskOut(BaseModel):
    id: int
    title: str
    module_id: int
    status: str

class Config:
    from_attributes = True