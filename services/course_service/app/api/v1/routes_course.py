from fastapi import APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.module import Module
from app.schemas.module import ModuleCreate, ModuleOut

router = APIRouter()

@router.get("/modules/{module_id}", response_model=dict)
async def get_module(module_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Module).where(Module.id == module_id))
    m = res.scalar_one_or_none()
    if not m:
        return {"error": "not found"}
    return {"id": m.id, "title": m.title}

@router.post("/modules", response_model=ModuleOut, status_code=201)
async def create_module(payload: ModuleCreate, db: AsyncSession = Depends(get_db)):
    stmt = insert(Module).values(title=payload.title).returning(Module.id, Module.title)
    res = await db.execute(stmt)
    row = res.first()
    await db.commit()
    return {"id": row.id, "title": row.title}

