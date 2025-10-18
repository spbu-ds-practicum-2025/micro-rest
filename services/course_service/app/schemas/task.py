from pydantic import BaseModel

class TaskBase(BaseModel):
    module_id: int
    question: str

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int

