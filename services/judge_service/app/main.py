from __future__ import annotations

import uuid
from typing import List

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID as UUIDType

from . import crud, executor, models, schemas
from .database import Base, engine, get_db

# Создаём таблицу submissions, если её ещё нет.
# tasks и test_cases уже созданы скриптом course_db.sql,
# create_all их повторно не тронет.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Judge Service",
    description="Сервис проверки посылок по задачам курса.",
    version="1.0.0",
)


# --------- Вспомогательные штуки ---------


def build_error(code: str, message: str) -> dict:
    err = schemas.ErrorResponse(
        errorId=str(uuid.uuid4()),
        code=code,
        message=message,
        details={},
    )
    return err.model_dump()


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(
    request: Request, exc: HTTPException
):
    # Если detail — наш ErrorResponse, возвращаем его как есть,
    # без обёртки {"detail": ...}
    if isinstance(exc.detail, dict) and "errorId" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return await http_exception_handler(request, exc)


def submission_to_schema(submission: models.Submission) -> schemas.Submission:
    return schemas.Submission(
        id=str(submission.id),
        taskId=str(submission.task_id),
        status=submission.status,  # строка, но Pydantic сам приведёт к Enum
        score=submission.score,
        language=submission.language,
        createdAt=submission.created_at,
        updatedAt=submission.updated_at,
    )


# --------- Ручки ---------


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get(
    "/tasks/{task_id}/submissions",
    response_model=List[schemas.Submission],
)
def list_submissions_by_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail=build_error("RESOURCE_NOT_FOUND", "Задача не найдена"),
        )

    submissions = crud.list_submissions_by_task(db, task_id)
    return [submission_to_schema(s) for s in submissions]


@app.post(
    "/tasks/{task_id}/submissions",
    response_model=schemas.Submission,
    status_code=201,
)
def create_submission(
    task_id: int,
    body: schemas.SubmissionCreateRequest,
    db: Session = Depends(get_db),
    x_idempotency_key: str = Header(
        ..., alias="X-Idempotency-Key"
    ),
):
    # Поддерживаем только python
    if body.language.lower() != "python":
        raise HTTPException(
            status_code=400,
            detail=build_error(
                "UNSUPPORTED_LANGUAGE",
                "Сейчас поддерживается только язык python.",
            ),
        )

    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail=build_error("RESOURCE_NOT_FOUND", "Задача не найдена"),
        )

    # Идемпотентность: если уже есть посылка с таким ключом — вернём её
    existing = crud.get_submission_by_idempotency(
        db, task_id, x_idempotency_key
    )
    if existing:
        return submission_to_schema(existing)

    # Создаём посылку со статусом RUNNING
    submission = crud.create_submission(
        db=db,
        task_id=task_id,
        code=body.code,
        language=body.language,
        status="RUNNING",
        score=None,
        idem_key=x_idempotency_key,
    )

    # Забираем тесты
    test_cases = crud.get_test_cases_for_task(db, task_id)

    # Гоним код по тестам
    passed, score = executor.run_python_code_against_tests(
        body.code, test_cases
    )
    final_status = "PASSED" if passed else "FAILED"

    submission = crud.update_submission_status(
        db, submission, final_status, score
    )

    return submission_to_schema(submission)


@app.get(
    "/submissions/{submission_id}",
    response_model=schemas.Submission,
)
def get_submission(
    submission_id: UUIDType,
    db: Session = Depends(get_db),
):
    submission = crud.get_submission_by_id(db, submission_id)
    if not submission:
        raise HTTPException(
            status_code=404,
            detail=build_error(
                "RESOURCE_NOT_FOUND", "Посылка не найдена"
            ),
        )

    return submission_to_schema(submission)
