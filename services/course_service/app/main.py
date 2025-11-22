from uuid import uuid4
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Depends, HTTPException, Path, Header, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.base import Base  # noqa: F401  # важно, чтобы модели были импортированы

from app.models.module import Module
from app.models.task import Task
from app.schemas.module import ModuleOut
from app.schemas.task import TaskOut
from app.schemas.error import ErrorResponse


# =========================================================
#  Работа с БД
# =========================================================

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
#  Приложение
# =========================================================

app = FastAPI(
    title="Course Service",
    description="Сервис курса: модули и задачи. Работает поверх БД из course_db.sql.",
    version="1.0.0",
)


# =========================================================
#  Хелперы
# =========================================================

def _short_description(text: str, max_len: int = 200) -> str:
    """
    Делаем из полного content короткое описание для поля description в Module.
    """
    if not text:
        return ""
    stripped = text.strip().replace("\r\n", "\n")
    if len(stripped) <= max_len:
        return stripped
    truncated = stripped[:max_len]
    last_space = truncated.rfind(" ")
    if last_space == -1:
        return truncated + "..."
    return truncated[:last_space] + "..."


def module_to_schema(m: Module) -> ModuleOut:
    """
    Маппинг SQLAlchemy-модели Module -> Pydantic-схема ModuleOut
    под контракт course.api.
    """
    return ModuleOut(
        id=m.id,
        title=m.title,
        description=m.content,
        order=m.order_index,
        # В схемe БД нет информации о прочитанности модулей пользователем,
        # поэтому пока всегда false.
        isRead=False,
        content=m.content
    )


def task_to_schema(t: Task) -> TaskOut:
    """
    Маппинг SQLAlchemy-модели Task -> Pydantic-схема TaskOut.
    maxScore берём константой (например, 100).
    """
    return TaskOut(
        id=t.id,
        moduleId=t.module_id,
        title=t.title,
        description=t.description,
        maxScore=100,
    )


# =========================================================
#  Обработчики ошибок: ErrorResponse
# =========================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code: Optional[str]
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        code = "RESOURCE_NOT_FOUND"
    elif exc.status_code == status.HTTP_400_BAD_REQUEST:
        code = "BAD_REQUEST"
    elif exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        code = "VALIDATION_ERROR"
    else:
        code = "HTTP_ERROR"

    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    error = ErrorResponse(
        errorId=uuid4(),
        code=code,
        message=message,
        details=None,
    )
    return JSONResponse(status_code=exc.status_code, content=error.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = ErrorResponse(
        errorId=uuid4(),
        code="VALIDATION_ERROR",
        message="Validation error",
        details={"errors": exc.errors()},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    error = ErrorResponse(
        errorId=uuid4(),
        code="INTERNAL_SERVER_ERROR",
        message="Internal server error",
        details=None,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump(),
    )


# =========================================================
#  Служебный эндпоинт
# =========================================================

@app.get("/healthz", summary="Healthcheck", tags=["Service"])
def healthz() -> Dict[str, Any]:
    return {"status": "ok", "service": "course"}


# =========================================================
#  Modules
# =========================================================

@app.get(
    "/modules",
    response_model=List[ModuleOut],
    summary="Получить список модулей",
    tags=["Modules"],
)
def list_modules(db: Session = Depends(get_db)) -> List[ModuleOut]:
    """
    Читает все модули из таблицы modules, сортирует по order_index.
    """
    modules = db.query(Module).order_by(Module.order_index).all()
    return [module_to_schema(m) for m in modules]


@app.get(
    "/modules/{module_id}",
    response_model=ModuleOut,
    summary="Получить модуль",
    tags=["Modules"],
)
def get_module(
    module_id: int = Path(..., ge=1, description="ID модуля (целое число >= 1)"),
    db: Session = Depends(get_db),
) -> ModuleOut:
    """
    Возвращает один модуль по ID. Если нет — 404 в формате ErrorResponse.
    """
    m: Optional[Module] = db.query(Module).filter(Module.id == module_id).first()
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")
    return module_to_schema(m)


@app.post(
    "/modules/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отметить модуль как прочитанный",
    tags=["Modules"],
)
def mark_module_read(
    module_id: int = Path(..., ge=1, description="ID модуля (целое число >= 1)"),
    idempotency_key: str = Header(
        ...,
        alias="X-Idempotency-Key",
        description="Уникальный идентификатор запроса для обеспечения идемпотентности",
    ),
    db: Session = Depends(get_db),
) -> None:
    """
    По контракту это “отметить модуль прочитанным”.
    В текущей схеме БД такого состояния нет, поэтому:
    - проверяем, что модуль существует;
    - если нет — 404;
    - если есть — просто возвращаем 204 No Content.
    """
    m: Optional[Module] = db.query(Module).filter(Module.id == module_id).first()
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found")

    # Здесь могла бы быть логика сохранения fact "прочитанности" в отдельную таблицу.
    return None


# =========================================================
#  Tasks
# =========================================================

@app.get(
    "/tasks",
    response_model=List[TaskOut],
    summary="Получить список задач",
    tags=["Tasks"],
)
def list_tasks(db: Session = Depends(get_db)) -> List[TaskOut]:
    """
    Возвращает список всех задач из таблицы tasks.
    """
    tasks = db.query(Task).order_by(Task.order_index).all()
    return [task_to_schema(t) for t in tasks]


@app.get(
    "/tasks/{task_id}",
    response_model=TaskOut,
    summary="Получить задачу",
    tags=["Tasks"],
)
def get_task(
    task_id: int = Path(..., ge=1, description="ID задачи (целое число >= 1)"),
    db: Session = Depends(get_db),
) -> TaskOut:
    """
    Возвращает задачу по ID. Если нет — 404 в формате ErrorResponse.
    """
    t: Optional[Task] = db.query(Task).filter(Task.id == task_id).first()
    if t is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_schema(t)
