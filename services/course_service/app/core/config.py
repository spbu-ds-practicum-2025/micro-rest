import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    app_name: str = "Course Service"
    api_prefix: str = "/api/course"
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@course_db:5432/course")

settings = Settings()