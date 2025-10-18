from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey
from app.db.base_class import Base

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id"), index=True, nullable=False)
    question: Mapped[str] = mapped_column(String(500), nullable="tasks")

    module: Mapped["Module"] = relationship(back_populates="tasks")