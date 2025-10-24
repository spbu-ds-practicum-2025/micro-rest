from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Submission(Base):
    __tablename__ = 'submissions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    status = Column(String(50), default='pending')
    execution_time = Column(Float)
    memory_used = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL', 'postgresql://judge_user:judge_password@judge_db:5432/judge_db')
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_submission(self, user_id: int, task_id: int, code: str) -> int:
        """Создать новую запись отправки"""
        session = self.Session()
        try:
            submission = Submission(
                user_id=user_id,
                task_id=task_id,
                code=code,
                status='evaluating'
            )
            session.add(submission)
            session.commit()
            return submission.id
        finally:
            session.close()

    def update_submission(self, submission_id: int, status: str,
                          execution_time: float = None, memory_used: int = None,
                          error_message: str = None):
        """Обновить запись отправки"""
        session = self.Session()
        try:
            submission = session.query(Submission).filter_by(id=submission_id).first()
            if submission:
                submission.status = status
                submission.execution_time = execution_time
                submission.memory_used = memory_used
                submission.error_message = error_message
                session.commit()
        finally:
            session.close()

    def get_user_submissions(self, user_id: int):
        """Получить все отправки пользователя"""
        session = self.Session()
        try:
            submissions = session.query(Submission).filter_by(user_id=user_id).order_by(
                Submission.created_at.desc()).all()
            return [
                {
                    'id': s.id,
                    'task_id': s.task_id,
                    'status': s.status,
                    'execution_time': s.execution_time,
                    'memory_used': s.memory_used,
                    'created_at': s.created_at.isoformat()
                }
                for s in submissions
            ]
        finally:
            session.close()