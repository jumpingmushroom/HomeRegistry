from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from ..database import Base


class LocationType(str, enum.Enum):
    HOME = "home"
    FLOOR = "floor"
    ROOM = "room"
    STORAGE = "storage"


class Location(Base):
    __tablename__ = "locations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    property_id = Column(String(36), ForeignKey("properties.id", ondelete="CASCADE"), nullable=True)
    parent_id = Column(String(36), ForeignKey("locations.id", ondelete="CASCADE"), nullable=True)
    location_type = Column(Enum(LocationType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    property = relationship("Property", back_populates="locations")
    parent = relationship("Location", remote_side=[id], backref="children")
    items = relationship("Item", back_populates="location", cascade="all, delete-orphan")
