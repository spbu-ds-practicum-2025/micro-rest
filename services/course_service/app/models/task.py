from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base




class Task(Base):
    __tablename__ = "tasks"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(32), nullable=False, default="todo")


    module = relationship("Module", backref="tasks")