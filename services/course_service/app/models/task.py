from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Task(Base):
    __tablename__ = "tasks"

    # course_db.sql: id bigint, module_id bigint, title, description, language, is_free, order_index
    id = Column(BigInteger, primary_key=True, index=True)
    module_id = Column(BigInteger, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    language = Column(String(50), nullable=False, default="python")
    is_free = Column(Boolean, nullable=False, default=False)
    order_index = Column(Integer, nullable=False, default=1)

    module = relationship("Module", back_populates="tasks")
