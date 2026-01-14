from sqlalchemy import Column, String, Text, Numeric, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..database import Base


class PolicyType(str, enum.Enum):
    HOMEOWNERS = "homeowners"
    RENTERS = "renters"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    UMBRELLA = "umbrella"
    CONTENTS = "contents"
    BUILDING = "building"
    OTHER = "other"


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)

    # Required fields
    name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    policy_number = Column(String(100), nullable=False)
    policy_type = Column(Enum(PolicyType), nullable=False)

    # Financial fields
    coverage_amount = Column(Numeric(12, 2), nullable=True)
    deductible = Column(Numeric(10, 2), nullable=True)
    premium = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(10), default="NOK")

    # Dates
    start_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)

    # Agent info
    agent_name = Column(String(255), nullable=True)
    agent_phone = Column(String(50), nullable=True)
    agent_email = Column(String(255), nullable=True)

    # Other
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="insurance_policies")
