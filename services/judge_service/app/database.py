import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# По умолчанию – как ты ходишь из хоста.
# В контейнере переопределяем через переменную окружения DATABASE_URL.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5433/course",
)

engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
