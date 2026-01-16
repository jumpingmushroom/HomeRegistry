"""
Service for checking warranty expirations and sending alert notifications.
"""
import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Set
from sqlalchemy.orm import Session

from ..config import settings
from ..models.item import Item
from ..models.warranty_alert import WarrantyAlert
from ..models.property import Property
from .email_service import email_service

logger = logging.getLogger(__name__)


class WarrantyService:
    """Service for warranty expiration checking and alerting."""

    def get_expiring_warranties(
        self,
        db: Session,
        days_threshold: int
    ) -> List[Item]:
        """
        Query items with warranties expiring within the threshold.

        Args:
            db: Database session
            days_threshold: Number of days to look ahead

        Returns:
            List of items with expiring warranties
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        items = db.query(Item).filter(
            Item.warranty_expiration.isnot(None),
            Item.warranty_expiration >= today,  # Not already expired
            Item.warranty_expiration <= threshold_date  # Within threshold
        ).all()

        return items

    def get_already_alerted_item_ids(
        self,
        db: Session,
        days_threshold: int
    ) -> Set[str]:
        """
        Get IDs of items that have already been alerted for this threshold.

        Args:
            db: Database session
            days_threshold: The alert threshold in days

        Returns:
            Set of item IDs that have already been alerted
        """
        alert_type = f"expiring_{days_threshold}_days"

        alerts = db.query(WarrantyAlert.item_id).filter(
            WarrantyAlert.alert_type == alert_type
        ).all()

        return {alert.item_id for alert in alerts}

    def prepare_items_for_email(
        self,
        db: Session,
        items: List[Item]
    ) -> List[Dict]:
        """
        Prepare item data for the email template.

        Args:
            db: Database session
            items: List of Item objects

        Returns:
            List of dicts with item info for email
        """
        today = date.today()
        prepared = []

        for item in items:
            days_remaining = (item.warranty_expiration - today).days

            # Get property name
            property_name = None
            if item.property_id:
                prop = db.query(Property).filter(Property.id == item.property_id).first()
                if prop:
                    property_name = prop.name

            prepared.append({
                "id": item.id,
                "name": item.name,
                "property_name": property_name or "N/A",
                "warranty_expiration": item.warranty_expiration.isoformat(),
                "days_remaining": days_remaining,
            })

        # Sort by days remaining (most urgent first)
        prepared.sort(key=lambda x: x["days_remaining"])

        return prepared

    def record_sent_alerts(
        self,
        db: Session,
        items: List[Item],
        days_threshold: int
    ) -> None:
        """
        Record that alerts have been sent for these items.

        Args:
            db: Database session
            items: List of items that were alerted
            days_threshold: The alert threshold used
        """
        alert_type = f"expiring_{days_threshold}_days"

        for item in items:
            alert = WarrantyAlert(
                item_id=item.id,
                alert_type=alert_type,
                warranty_expiration=item.warranty_expiration
            )
            db.add(alert)

        db.commit()
        logger.info(f"Recorded {len(items)} warranty alerts of type '{alert_type}'")

    def check_and_send_alerts(self, db: Session) -> Dict:
        """
        Main orchestration method: check for expiring warranties and send alerts.

        Args:
            db: Database session

        Returns:
            Dict with summary of actions taken
        """
        days_threshold = settings.warranty_alert_days_threshold
        result = {
            "checked": True,
            "threshold_days": days_threshold,
            "items_expiring": 0,
            "items_already_alerted": 0,
            "items_to_alert": 0,
            "email_sent": False,
            "alerts_recorded": 0,
        }

        # Get items with expiring warranties
        expiring_items = self.get_expiring_warranties(db, days_threshold)
        result["items_expiring"] = len(expiring_items)

        if not expiring_items:
            logger.info(f"No items with warranties expiring within {days_threshold} days")
            return result

        # Filter out already-alerted items
        already_alerted = self.get_already_alerted_item_ids(db, days_threshold)
        result["items_already_alerted"] = len(already_alerted)

        items_to_alert = [item for item in expiring_items if item.id not in already_alerted]
        result["items_to_alert"] = len(items_to_alert)

        if not items_to_alert:
            logger.info(f"All {len(expiring_items)} expiring items have already been alerted")
            return result

        # Prepare items for email
        prepared_items = self.prepare_items_for_email(db, items_to_alert)

        # Send digest email
        if email_service.is_configured():
            email_sent = email_service.send_warranty_expiration_alert(
                prepared_items,
                days_threshold
            )
            result["email_sent"] = email_sent

            if email_sent:
                # Record alerts only if email was sent
                self.record_sent_alerts(db, items_to_alert, days_threshold)
                result["alerts_recorded"] = len(items_to_alert)
                logger.info(
                    f"Warranty alert sent for {len(items_to_alert)} items "
                    f"expiring within {days_threshold} days"
                )
            else:
                logger.error("Failed to send warranty alert email")
        else:
            logger.warning("Email not configured, skipping warranty alerts")

        return result


# Singleton instance
warranty_service = WarrantyService()
