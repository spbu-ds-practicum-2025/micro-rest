from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.base import Base # подтянет модели

from app.models.module import Module
from app.schemas.module import ModuleOut, ModuleCreate


app = FastAPI(title="Course Service", version="0.2.0")
# Создаём таблицы при старте (для прототипа). На проде лучше Alembic.
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.get("/healthz")
def healthz():
    return {"status": "ok"}




# ───────────────────── Модули ─────────────────────
@app.get("/api/course/modules", response_model=List[ModuleOut])
def list_modules(
        skip: int = 0,
        limit: int = Query(50, le=200),
        db: Session = Depends(get_db),
    ):
    q = db.query(Module).offset(skip).limit(limit)
    return q.all()




@app.get("/api/course/modules/{module_id}", response_model=ModuleOut)
def get_module(module_id: int, db: Session = Depends(get_db)):
    m = db.get(Module, module_id)
    if not m:
        raise HTTPException(status_code=404, detail="Module not found")
    return m




@app.post("/api/course/modules", status_code=201, response_model=ModuleOut)
def create_module(payload: ModuleCreate, db: Session = Depends(get_db)):
    # На будущее: ты планируешь наполнять через DBeaver, но POST оставим для удобства тестов
    m = Module(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m