from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImageResponse(BaseModel):
    id: str
    item_id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    is_primary: bool
    ai_analysis: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ImageAnalysisRequest(BaseModel):
    """Request schema for analyzing images before creating an item"""
    pass  # Images will be uploaded as multipart/form-data


class AIAnalysisResult(BaseModel):
    item_name: str
    category: str
    description: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    condition: str = "good"
    estimated_value_nok: Optional[float] = None
    suggested_location: Optional[str] = None
    key_features: List[str] = []
    warranty_info: Optional[str] = None
    confidence_score: float = 0.0


class ImageAnalysisResponse(BaseModel):
    success: bool
    analysis: Optional[AIAnalysisResult] = None
    error: Optional[str] = None
    image_count: int = 0
