"""
Warranty alert scheduler using APScheduler.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from ..config import settings
from ..database import SessionLocal
from .warranty_service import warranty_service

logger = logging.getLogger(__name__)


class WarrantyScheduler:
    """Scheduler for automatic warranty expiration checks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
        self._job_id = "warranty_check_job"

    def _run_warranty_check(self) -> None:
        """Execute warranty check job with error handling."""
        logger.info("Starting scheduled warranty check...")

        db = SessionLocal()
        try:
            result = warranty_service.check_and_send_alerts(db)
            logger.info(
                f"Scheduled warranty check completed: "
                f"{result['items_to_alert']} new alerts, "
                f"{result['items_already_alerted']} previously alerted, "
                f"email_sent={result['email_sent']}"
            )

        except Exception as e:
            logger.error(f"Scheduled warranty check failed: {e}")

        finally:
            db.close()

    def start(self) -> None:
        """Start the warranty scheduler if enabled."""
        if not settings.warranty_alerts_enabled:
            logger.info("Warranty alert scheduler disabled via configuration")
            return

        if self._is_running:
            logger.warning("Warranty scheduler already running")
            return

        # Schedule to run daily at the configured hour
        check_hour = settings.warranty_alert_check_hour

        self.scheduler.add_job(
            self._run_warranty_check,
            trigger=CronTrigger(hour=check_hour, minute=0),
            id=self._job_id,
            name="Warranty Expiration Check",
            replace_existing=True
        )

        self.scheduler.start()
        self._is_running = True

        logger.info(
            f"Warranty scheduler started (daily at {check_hour:02d}:00)"
        )

    def stop(self) -> None:
        """Stop the warranty scheduler."""
        if not self._is_running:
            return

        try:
            self.scheduler.remove_job(self._job_id)
        except Exception:
            pass

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

        self._is_running = False
        logger.info("Warranty scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running

    def run_now(self) -> dict:
        """Trigger an immediate warranty check (outside scheduler)."""
        logger.info("Manual warranty check triggered")

        db = SessionLocal()
        try:
            result = warranty_service.check_and_send_alerts(db)
            return result
        finally:
            db.close()


# Singleton instance
warranty_scheduler = WarrantyScheduler()
