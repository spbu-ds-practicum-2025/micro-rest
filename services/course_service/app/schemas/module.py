from pydantic import BaseModel

class ModuleBase(BaseModel):
    titile: str

class ModuleCreate(ModuleBase):
    pass

class ModuleOut(ModuleBase):
    id: int

