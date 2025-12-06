import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID

from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, index=True)
    module_id = Column(BigInteger, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    language = Column(String(50), nullable=False, server_default="python")
    is_free = Column(Boolean, nullable=False, server_default="false")
    order_index = Column(Integer, nullable=False, server_default="1")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(BigInteger, primary_key=True, index=True)
    task_id = Column(
        BigInteger,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)


class Submission(Base):
    """
    Таблица для посылок.

    Имена и поля подобраны под схемы из course_api.yaml:
    - status: QUEUED / RUNNING / PASSED / FAILED
    - score: int или null
    - language: строка
    """

    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "idempotency_key",
            name="uq_submissions_task_id_idem_key",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    task_id = Column(
        BigInteger,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    score = Column(Integer, nullable=True)
    idempotency_key = Column(String(64), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
