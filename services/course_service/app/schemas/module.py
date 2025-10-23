from pydantic import BaseModel, HttpUrl
from typing import Optional


class ModuleCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: Optional[HttpUrl | str] = None




class ModuleOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None


class Config:
    from_attributes = True # pydantic v2
