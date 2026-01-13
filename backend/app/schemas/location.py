from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.location import LocationType


class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None
    location_type: LocationType
    parent_id: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location_type: Optional[LocationType] = None
    parent_id: Optional[str] = None


class LocationResponse(LocationBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    item_count: int = 0

    class Config:
        from_attributes = True


class LocationTree(LocationResponse):
    children: List["LocationTree"] = []

    class Config:
        from_attributes = True
