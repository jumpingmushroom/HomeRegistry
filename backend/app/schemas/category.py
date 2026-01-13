from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: str
    created_at: datetime
    item_count: int = 0

    class Config:
        from_attributes = True


class CategoryTree(CategoryResponse):
    children: List["CategoryTree"] = []

    class Config:
        from_attributes = True
