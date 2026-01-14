from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from ..models.property import PropertyType


class PropertyBase(BaseModel):
    name: str
    address_street: str
    address_city: str
    address_state: str
    address_postal_code: str
    address_country: str
    primary_contact_name: str
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    additional_residents: Optional[str] = None
    property_type: Optional[PropertyType] = PropertyType.HOUSE
    year_built: Optional[int] = None
    square_meters: Optional[int] = None
    notes: Optional[str] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    additional_residents: Optional[str] = None
    property_type: Optional[PropertyType] = None
    year_built: Optional[int] = None
    square_meters: Optional[int] = None
    notes: Optional[str] = None


class InsurancePolicySummary(BaseModel):
    id: str
    name: str
    company_name: str
    policy_type: str
    renewal_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class PropertyResponse(PropertyBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    insurance_policies: List[Any] = []

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    id: str
    name: str
    address_city: str
    address_country: str
    property_type: Optional[PropertyType] = None
    policy_count: int = 0

    class Config:
        from_attributes = True
