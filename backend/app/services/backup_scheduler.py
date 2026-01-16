"""
Backup scheduler using APScheduler.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..config import settings
from .backup_service import backup_service
from .email_service import email_service

logger = logging.getLogger(__name__)


class BackupScheduler:
    """Scheduler for automatic database backups."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
        self._job_id = "backup_job"

    def _run_backup(self) -> None:
        """Execute backup job with error handling and email alerts."""
        logger.info("Starting scheduled backup...")

        try:
            result = backup_service.create_backup()
            logger.info(
                f"Scheduled backup completed: {result['filename']} "
                f"({result['size']} bytes)"
            )

        except FileNotFoundError as e:
            error_msg = f"Database not found: {e}"
            logger.error(f"Scheduled backup failed: {error_msg}")
            self._send_failure_alert(error_msg)

        except IOError as e:
            error_msg = f"IO error during backup: {e}"
            logger.error(f"Scheduled backup failed: {error_msg}")
            self._send_failure_alert(error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(f"Scheduled backup failed: {error_msg}")
            self._send_failure_alert(error_msg)

    def _send_failure_alert(self, error_message: str) -> None:
        """Send email alert on backup failure if configured."""
        if email_service.is_configured():
            try:
                email_service.send_backup_failure_alert(error_message)
            except Exception as e:
                logger.error(f"Failed to send backup failure alert: {e}")
        else:
            logger.debug("Email not configured, skipping failure alert")

    def start(self) -> None:
        """Start the backup scheduler if enabled."""
        if not settings.backup_enabled:
            logger.info("Backup scheduler disabled via configuration")
            return

        if self._is_running:
            logger.warning("Backup scheduler already running")
            return

        # Add backup job with configured interval
        interval_hours = settings.backup_interval_hours

        self.scheduler.add_job(
            self._run_backup,
            trigger=IntervalTrigger(hours=interval_hours),
            id=self._job_id,
            name="Database Backup",
            replace_existing=True
        )

        self.scheduler.start()
        self._is_running = True

        logger.info(
            f"Backup scheduler started (interval: {interval_hours} hour(s))"
        )

    def stop(self) -> None:
        """Stop the backup scheduler."""
        if not self._is_running:
            return

        try:
            self.scheduler.remove_job(self._job_id)
        except Exception:
            pass

        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

        self._is_running = False
        logger.info("Backup scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running

    def run_now(self) -> None:
        """Trigger an immediate backup (outside scheduler)."""
        self._run_backup()


# Singleton instance
backup_scheduler = BackupScheduler()
