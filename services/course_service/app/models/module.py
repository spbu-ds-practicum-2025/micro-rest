from sqlalchemy import Column, Integer, BigInteger, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Module(Base):
    __tablename__ = "modules"

    # course_db.sql: id bigint, title varchar(255), content text, order_index int
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    order_index = Column(Integer, nullable=False)

    # Связь с задачами
    tasks = relationship("Task", back_populates="module")
