from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date
from decimal import Decimal
from ..models.item import ItemCondition


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    property_id: Optional[str] = None
    category_id: Optional[str] = None
    location_id: Optional[str] = None
    serial_number: Optional[str] = None
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None
    condition: Optional[ItemCondition] = None
    quantity: int = 1
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    purchase_location: Optional[str] = None
    current_value: Optional[Decimal] = None
    currency: str = "NOK"
    warranty_expiration: Optional[date] = None
    barcode: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class ItemCreate(ItemBase):
    ai_metadata: Optional[dict] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    property_id: Optional[str] = None
    category_id: Optional[str] = None
    location_id: Optional[str] = None
    serial_number: Optional[str] = None
    model_number: Optional[str] = None
    manufacturer: Optional[str] = None
    condition: Optional[ItemCondition] = None
    quantity: Optional[int] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    purchase_location: Optional[str] = None
    current_value: Optional[Decimal] = None
    currency: Optional[str] = None
    warranty_expiration: Optional[date] = None
    barcode: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    ai_metadata: Optional[dict] = None


class ItemResponse(ItemBase):
    id: str
    ai_metadata: Optional[dict] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: List[Any] = []  # Will be ImageResponse
    documents: List[Any] = []  # Will be DocumentResponse
    property_name: Optional[str] = None
    category_name: Optional[str] = None
    location_name: Optional[str] = None

    class Config:
        from_attributes = True


class ItemListResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    page_size: int


class BatchUpdateRequest(BaseModel):
    """Request to batch update multiple items"""
    item_ids: List[str]
    location_id: Optional[str] = None
    condition: Optional[ItemCondition] = None
    category_id: Optional[str] = None
    property_id: Optional[str] = None


class BatchDeleteRequest(BaseModel):
    """Request to batch delete multiple items"""
    item_ids: List[str]


class BatchUpdateResponse(BaseModel):
    """Response from batch update operation"""
    updated_count: int
    item_ids: List[str]


class BatchDeleteResponse(BaseModel):
    """Response from batch delete operation"""
    deleted_count: int
    item_ids: List[str]
