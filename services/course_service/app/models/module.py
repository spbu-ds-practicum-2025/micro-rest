from sqlalchemy import Column, Integer, String, Text
from app.db.base_class import Base




class Module(Base):
    __tablename__ = "modules"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    