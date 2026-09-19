from pydantic import BaseModel, Field
from typing import Optional, Any
from enum import Enum
from datetime import datetime

class TaskTypeEnum(str, Enum):
    sentiment_analysis = "sentiment_analysis"
    named_entity_recognition = "named_entity_recognition"

class TaskCreateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="The text content to be processed")
    task_type: TaskTypeEnum = Field(..., description="The NLP task to perform")

class TaskResponse(BaseModel):
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    updated_at: datetime
