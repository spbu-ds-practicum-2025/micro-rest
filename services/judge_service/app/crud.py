from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from . import models


def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_test_cases_for_task(
    db: Session, task_id: int
) -> List[models.TestCase]:
    return (
        db.query(models.TestCase)
        .filter(models.TestCase.task_id == task_id)
        .order_by(models.TestCase.id)
        .all()
    )


def get_submission_by_id(
    db: Session, submission_id: UUID
) -> Optional[models.Submission]:
    return (
        db.query(models.Submission)
        .filter(models.Submission.id == submission_id)
        .first()
    )


def get_submission_by_idempotency(
    db: Session, task_id: int, idem_key: str
) -> Optional[models.Submission]:
    return (
        db.query(models.Submission)
        .filter(
            models.Submission.task_id == task_id,
            models.Submission.idempotency_key == idem_key,
        )
        .first()
    )


def list_submissions_by_task(
    db: Session, task_id: int
) -> List[models.Submission]:
    return (
        db.query(models.Submission)
        .filter(models.Submission.task_id == task_id)
        .order_by(models.Submission.created_at.desc())
        .all()
    )


def create_submission(
    db: Session,
    task_id: int,
    code: str,
    language: str,
    status: str,
    score: int | None,
    idem_key: str | None,
) -> models.Submission:
    submission = models.Submission(
        task_id=task_id,
        code=code,
        language=language,
        status=status,
        score=score,
        idempotency_key=idem_key,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def update_submission_status(
    db: Session,
    submission: models.Submission,
    status: str,
    score: int | None,
) -> models.Submission:
    submission.status = status
    submission.score = score
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
