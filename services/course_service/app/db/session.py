import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_SYNC_URL = os.getenv(
"DATABASE_SYNC_URL",
"postgresql+psycopg://postgres:postgres@course_db:5432/course",
)


engine = create_engine(
DATABASE_SYNC_URL,
pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)