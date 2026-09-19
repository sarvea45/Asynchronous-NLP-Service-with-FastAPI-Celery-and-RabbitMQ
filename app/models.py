import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, JSON, DateTime
from app.database import Base

class NLPTask(Base):
    __tablename__ = "nlp_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    input_text = Column(Text, nullable=False)
    task_type = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="PENDING")
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
