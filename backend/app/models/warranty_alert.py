"""
Model for tracking warranty expiration alerts to prevent duplicate notifications.
"""
from sqlalchemy import Column, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database import Base


class WarrantyAlert(Base):
    """Track sent warranty alerts to prevent duplicate notifications."""
    __tablename__ = "warranty_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # e.g., "expiring_30_days"
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    warranty_expiration = Column(Date, nullable=False)  # snapshot of expiration at alert time

    # Relationship
    item = relationship("Item")
