from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.routes_course import router as course_router

app = FastAPI(title=settings.app_name)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

app.include_router(course_router, prefix=settings.api_prefix)