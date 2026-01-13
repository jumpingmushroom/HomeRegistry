from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models.setting import Setting
from ..schemas.setting import SettingUpdate, SettingResponse, TestAIRequest, TestAIResponse
from ..services.ai import ClaudeProvider, OpenAIProvider, OllamaProvider, GeminiProvider

router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_setting_value(db: Session, key: str, default: any = None) -> any:
    """Get setting value from database"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting else default


def set_setting_value(db: Session, key: str, value: any):
    """Set setting value in database"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()


@router.get("", response_model=SettingResponse)
async def get_settings(db: Session = Depends(get_db)):
    """Get all settings"""
    ai_provider = get_setting_value(db, "ai_provider", "claude")
    claude_key = get_setting_value(db, "claude_api_key")
    openai_key = get_setting_value(db, "openai_api_key")
    gemini_key = get_setting_value(db, "gemini_api_key")
    ollama_endpoint = get_setting_value(db, "ollama_endpoint", "http://ollama:11434")
    default_currency = get_setting_value(db, "default_currency", "NOK")
    setup_completed = get_setting_value(db, "setup_completed", False)

    return SettingResponse(
        ai_provider=ai_provider,
        claude_api_key=claude_key,
        openai_api_key=openai_key,
        gemini_api_key=gemini_key,
        ollama_endpoint=ollama_endpoint,
        default_currency=default_currency,
        setup_completed=setup_completed
    )


@router.put("", response_model=SettingResponse)
async def update_settings(settings: SettingUpdate, db: Session = Depends(get_db)):
    """Update settings"""
    if settings.ai_provider is not None:
        set_setting_value(db, "ai_provider", settings.ai_provider)

    if settings.claude_api_key is not None:
        set_setting_value(db, "claude_api_key", settings.claude_api_key)

    if settings.openai_api_key is not None:
        set_setting_value(db, "openai_api_key", settings.openai_api_key)

    if settings.gemini_api_key is not None:
        set_setting_value(db, "gemini_api_key", settings.gemini_api_key)

    if settings.ollama_endpoint is not None:
        set_setting_value(db, "ollama_endpoint", settings.ollama_endpoint)

    if settings.default_currency is not None:
        set_setting_value(db, "default_currency", settings.default_currency)

    if settings.setup_completed is not None:
        set_setting_value(db, "setup_completed", settings.setup_completed)

    return await get_settings(db)


@router.post("/test-ai", response_model=TestAIResponse)
async def test_ai_connection(request: TestAIRequest):
    """Test AI provider connection"""
    try:
        if request.provider == "claude":
            if not request.api_key:
                return TestAIResponse(success=False, message="API key required for Claude")
            provider = ClaudeProvider(request.api_key)
        elif request.provider == "openai":
            if not request.api_key:
                return TestAIResponse(success=False, message="API key required for OpenAI")
            provider = OpenAIProvider(request.api_key)
        elif request.provider == "gemini":
            if not request.api_key:
                return TestAIResponse(success=False, message="API key required for Gemini")
            provider = GeminiProvider(request.api_key)
        elif request.provider == "ollama":
            endpoint = request.endpoint or "http://ollama:11434"
            provider = OllamaProvider(endpoint)
        else:
            return TestAIResponse(success=False, message=f"Unknown provider: {request.provider}")

        success, message = await provider.test_connection()
        return TestAIResponse(success=success, message=message)

    except Exception as e:
        return TestAIResponse(success=False, message=str(e))
