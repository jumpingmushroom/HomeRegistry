from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class SettingUpdate(BaseModel):
    ai_provider: Optional[str] = None
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_endpoint: Optional[str] = None
    default_currency: Optional[str] = None
    setup_completed: Optional[bool] = None


class SettingResponse(BaseModel):
    ai_provider: str
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ollama_endpoint: str
    default_currency: str
    setup_completed: bool = False


class TestAIRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


class TestAIResponse(BaseModel):
    success: bool
    message: str
