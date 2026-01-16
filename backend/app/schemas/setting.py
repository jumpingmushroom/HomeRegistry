from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime


class SettingUpdate(BaseModel):
    ai_provider: Optional[str] = None
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    ollama_endpoint: Optional[str] = None
    default_currency: Optional[str] = None
    setup_completed: Optional[bool] = None
    high_value_threshold: Optional[int] = None


class SettingResponse(BaseModel):
    ai_provider: str
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    gemini_model: Optional[str] = None
    ollama_endpoint: str
    default_currency: str
    setup_completed: bool = False
    high_value_threshold: int = 5000


class TestAIRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


class GeminiModel(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    supports_vision: bool


class TestAIResponse(BaseModel):
    success: bool
    message: str
    available_models: Optional[List[GeminiModel]] = None
