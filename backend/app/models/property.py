from sqlalchemy import Column, String, Text, Integer, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..database import Base


class PropertyType(str, enum.Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    CABIN = "cabin"
    STORAGE_UNIT = "storage_unit"
    OTHER = "other"


class Property(Base):
    __tablename__ = "properties"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Required fields
    name = Column(String(255), nullable=False)
    address_street = Column(String(255), nullable=False)
    address_city = Column(String(255), nullable=False)
    address_state = Column(String(255), nullable=False)
    address_postal_code = Column(String(50), nullable=False)
    address_country = Column(String(100), nullable=False)
    primary_contact_name = Column(String(255), nullable=False)

    # Optional fields
    primary_contact_email = Column(String(255), nullable=True)
    primary_contact_phone = Column(String(50), nullable=True)
    additional_residents = Column(Text, nullable=True)
    property_type = Column(Enum(PropertyType), nullable=True, default=PropertyType.HOUSE)
    year_built = Column(Integer, nullable=True)
    square_meters = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    insurance_policies = relationship("InsurancePolicy", back_populates="property", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="property", cascade="all, delete-orphan")
    locations = relationship("Location", back_populates="property", cascade="all, delete-orphan")
