from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import docker
from .judge import PythonJudge
from .database import DatabaseManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Judge Service", version="1.0.0")

# Инициализация компонентов
db_manager = DatabaseManager()
docker_client = docker.from_env()
judge = PythonJudge(docker_client, db_manager)

class SubmissionRequest(BaseModel):
    user_id: int
    task_id: int
    code: str
    time_limit: int = 5
    memory_limit: int = 128

class SubmissionResponse(BaseModel):
    submission_id: int
    status: str
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    error_message: Optional[str] = None

@app.post("/submit", response_model=SubmissionResponse)
async def submit_solution(request: SubmissionRequest):
    """Принять решение на проверку"""
    try:
        result = await judge.evaluate_submission(
            user_id=request.user_id,
            task_id=request.task_id,
            code=request.code,
            time_limit=request.time_limit,
            memory_limit=request.memory_limit
        )
        return result
    except Exception as e:
        logger.error(f"Error processing submission: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/submissions/{user_id}")
async def get_user_submissions(user_id: int):
    """Получить все решения пользователя"""
    try:
        submissions = db_manager.get_user_submissions(user_id)
        return {"user_id": user_id, "submissions": submissions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {"status": "healthy", "service": "judge_service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)