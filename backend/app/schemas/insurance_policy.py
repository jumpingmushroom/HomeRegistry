from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal
from ..models.insurance_policy import PolicyType


class InsurancePolicyBase(BaseModel):
    name: str
    company_name: str
    policy_number: str
    policy_type: PolicyType
    coverage_amount: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    currency: str = "NOK"
    start_date: Optional[date] = None
    renewal_date: Optional[date] = None
    agent_name: Optional[str] = None
    agent_phone: Optional[str] = None
    agent_email: Optional[str] = None
    notes: Optional[str] = None


class InsurancePolicyCreate(InsurancePolicyBase):
    property_id: str


class InsurancePolicyUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    policy_number: Optional[str] = None
    policy_type: Optional[PolicyType] = None
    coverage_amount: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    premium: Optional[Decimal] = None
    currency: Optional[str] = None
    start_date: Optional[date] = None
    renewal_date: Optional[date] = None
    agent_name: Optional[str] = None
    agent_phone: Optional[str] = None
    agent_email: Optional[str] = None
    notes: Optional[str] = None


class InsurancePolicyResponse(InsurancePolicyBase):
    id: str
    property_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    property_name: Optional[str] = None

    class Config:
        from_attributes = True
