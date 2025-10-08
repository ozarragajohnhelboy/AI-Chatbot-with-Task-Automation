from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(str, Enum):
    CHAT = "chat"
    FILE_OPERATION = "file_operation"
    SCHEDULE_REMINDER = "schedule_reminder"
    RUN_SCRIPT = "run_script"
    SEARCH = "search"
    SYSTEM_INFO = "system_info"
    EXCEL_OPERATION = "excel_operation"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Message(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class Intent(BaseModel):
    type: IntentType
    confidence: float
    entities: Dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    response: str
    intent: Intent
    session_id: str
    task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TaskRequest(BaseModel):
    task_type: str
    parameters: Dict[str, Any]
    schedule: Optional[str] = None


class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Conversation(BaseModel):
    session_id: str
    messages: List[Message]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LearningFeedback(BaseModel):
    session_id: str
    message: str
    expected_intent: IntentType
    expected_response: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)

