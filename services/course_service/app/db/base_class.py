# app/db/base_class.py
from sqlalchemy.orm import declarative_base

# class Base(DeclarativeBase):
#     """Единая база для всех моделей SQLAlchemy."""
#     pass

Base = declarative_base()