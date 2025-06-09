from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TaskCreate(BaseModel):
    assignee: str = Field(..., description="AI agent: claude, deepseek, or grok")
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    telegram_chat_id: int = Field(...)
    created_by: Optional[int] = Field(None)
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class TaskUpdate(BaseModel):
    status: Optional[str] = Field(None)
    output_data: Optional[Dict[str, Any]] = Field(None)
    title: Optional[str] = Field(None)

class TaskCompletion(BaseModel):
    output_data: Dict[str, Any] = Field(...)

class ClaudeResponse(BaseModel):
    response: str = Field(..., min_length=10)
    analysis_type: Optional[str] = Field("general")
    recommendations: Optional[list] = Field(default_factory=list)

class TaskResponse(BaseModel):
    id: str
    assignee: str
    title: str
    description: str
    status: str
    telegram_chat_id: int
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    input_data: Optional[Dict[str, Any]]
    output_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True

class APIResponse(BaseModel):
    id: Optional[str] = None
    status: str
    message: str
