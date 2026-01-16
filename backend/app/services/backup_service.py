"""
Database backup service with tiered retention policy.
"""
import os
import shutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

from ..config import settings

logger = logging.getLogger(__name__)


class BackupService:
    """Service for managing database backups with tiered retention."""

    APP_NAME = "homeregistry"

    def __init__(self):
        self.db_path = settings.database_url
        self.backup_dir = settings.backup_dir
        self._last_backup_time: Optional[datetime] = None
        self._last_backup_error: Optional[str] = None

    def _ensure_backup_dir(self) -> None:
        """Create backup directory if it doesn't exist."""
        os.makedirs(self.backup_dir, exist_ok=True)

    def _generate_filename(self) -> str:
        """Generate timestamped backup filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{self.APP_NAME}_backup_{timestamp}.db"

    def _parse_backup_datetime(self, filename: str) -> Optional[datetime]:
        """Parse datetime from backup filename."""
        try:
            # Expected format: homeregistry_backup_YYYYmmdd_HHMMSS.db
            parts = filename.replace(".db", "").split("_")
            if len(parts) >= 4:
                date_str = parts[-2]
                time_str = parts[-1]
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        except (ValueError, IndexError):
            pass
        return None

    def _is_valid_backup_file(self, filename: str) -> bool:
        """Check if filename matches expected backup pattern."""
        return (
            filename.startswith(f"{self.APP_NAME}_backup_") and
            filename.endswith(".db") and
            self._parse_backup_datetime(filename) is not None
        )

    def create_backup(self) -> Dict:
        """
        Create a backup of the database.

        Returns:
            Dict with backup metadata (filename, path, size, created_at)

        Raises:
            FileNotFoundError: If source database doesn't exist
            IOError: If backup fails
        """
        # Validate source database exists
        if not os.path.exists(self.db_path):
            self._last_backup_error = f"Source database not found: {self.db_path}"
            logger.error(self._last_backup_error)
            raise FileNotFoundError(self._last_backup_error)

        # Ensure backup directory exists
        self._ensure_backup_dir()

        # Generate filename and destination path
        filename = self._generate_filename()
        dest_path = os.path.join(self.backup_dir, filename)

        try:
            # Copy database file
            shutil.copy2(self.db_path, dest_path)

            # Get file stats
            stat = os.stat(dest_path)
            created_at = datetime.now()

            self._last_backup_time = created_at
            self._last_backup_error = None

            logger.info(f"Backup created: {filename} ({stat.st_size} bytes)")

            # Run cleanup after successful backup
            self.cleanup_old_backups()

            return {
                "filename": filename,
                "path": dest_path,
                "size": stat.st_size,
                "created_at": created_at.isoformat()
            }

        except Exception as e:
            self._last_backup_error = str(e)
            logger.error(f"Backup failed: {e}")
            raise IOError(f"Failed to create backup: {e}")

    def list_backups(self) -> List[Dict]:
        """
        List all available backups with metadata.

        Returns:
            List of dicts with backup info (filename, size, created_at)
        """
        backups = []

        if not os.path.exists(self.backup_dir):
            return backups

        for filename in os.listdir(self.backup_dir):
            if not self._is_valid_backup_file(filename):
                continue

            filepath = os.path.join(self.backup_dir, filename)
            if not os.path.isfile(filepath):
                continue

            stat = os.stat(filepath)
            backup_time = self._parse_backup_datetime(filename)

            backups.append({
                "filename": filename,
                "size": stat.st_size,
                "created_at": backup_time.isoformat() if backup_time else None
            })

        # Sort by creation time, newest first
        backups.sort(key=lambda x: x["created_at"] or "", reverse=True)
        return backups

    def get_backup_path(self, filename: str) -> Optional[str]:
        """
        Get full path for a backup file, with security validation.

        Args:
            filename: Name of the backup file

        Returns:
            Full path if valid, None if invalid or not found
        """
        # Security: Prevent path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            logger.warning(f"Path traversal attempt detected: {filename}")
            return None

        # Validate filename format
        if not self._is_valid_backup_file(filename):
            logger.warning(f"Invalid backup filename: {filename}")
            return None

        filepath = os.path.join(self.backup_dir, filename)

        # Security: Ensure resolved path is within backup directory
        resolved_path = os.path.realpath(filepath)
        resolved_backup_dir = os.path.realpath(self.backup_dir)

        if not resolved_path.startswith(resolved_backup_dir):
            logger.warning(f"Path escape attempt: {filename}")
            return None

        # Check file exists
        if not os.path.isfile(filepath):
            return None

        return filepath

    def get_current_db_path(self) -> str:
        """Get path to the current live database."""
        return self.db_path

    def cleanup_old_backups(self) -> Dict:
        """
        Apply tiered retention policy to remove old backups.

        Retention tiers:
        - Hourly: Keep all backups from last N hours (default 24)
        - Daily: Keep one per day for last N days (default 7), prefer midnight
        - Weekly: Keep one per week for last N weeks (default 4), prefer Sunday
        - Monthly: Keep one per month for last N months (default 12), prefer 1st

        Returns:
            Dict with cleanup stats (kept, deleted, errors)
        """
        now = datetime.now()

        # Get retention settings
        hourly_hours = settings.backup_retention_hourly
        daily_days = settings.backup_retention_daily
        weekly_weeks = settings.backup_retention_weekly
        monthly_months = settings.backup_retention_monthly

        # Calculate tier boundaries
        hourly_cutoff = now - timedelta(hours=hourly_hours)
        daily_cutoff = now - timedelta(days=daily_days)
        weekly_cutoff = now - timedelta(weeks=weekly_weeks)
        monthly_cutoff = now - timedelta(days=monthly_months * 31)  # Approximate

        # Collect all backups with their timestamps
        backups = []
        if os.path.exists(self.backup_dir):
            for filename in os.listdir(self.backup_dir):
                if not self._is_valid_backup_file(filename):
                    continue

                backup_time = self._parse_backup_datetime(filename)
                if backup_time:
                    backups.append({
                        "filename": filename,
                        "time": backup_time
                    })

        # Determine which backups to keep
        to_keep = set()

        # Tier 1: Keep all backups within hourly window
        for backup in backups:
            if backup["time"] >= hourly_cutoff:
                to_keep.add(backup["filename"])

        # Tier 2: Daily - keep one per day (prefer closest to midnight)
        daily_backups = defaultdict(list)
        for backup in backups:
            if hourly_cutoff > backup["time"] >= daily_cutoff:
                day_key = backup["time"].strftime("%Y-%m-%d")
                daily_backups[day_key].append(backup)

        for day, day_list in daily_backups.items():
            # Prefer backup closest to midnight (00:00:00)
            best = min(day_list, key=lambda b: abs(
                b["time"].hour * 3600 + b["time"].minute * 60 + b["time"].second
            ))
            to_keep.add(best["filename"])

        # Tier 3: Weekly - keep one per week (prefer Sunday)
        weekly_backups = defaultdict(list)
        for backup in backups:
            if daily_cutoff > backup["time"] >= weekly_cutoff:
                # ISO week number and year
                week_key = backup["time"].strftime("%Y-W%W")
                weekly_backups[week_key].append(backup)

        for week, week_list in weekly_backups.items():
            # Prefer Sunday (weekday 6)
            best = min(week_list, key=lambda b: abs(b["time"].weekday() - 6) % 7)
            to_keep.add(best["filename"])

        # Tier 4: Monthly - keep one per month (prefer 1st of month)
        monthly_backups = defaultdict(list)
        for backup in backups:
            if weekly_cutoff > backup["time"] >= monthly_cutoff:
                month_key = backup["time"].strftime("%Y-%m")
                monthly_backups[month_key].append(backup)

        for month, month_list in monthly_backups.items():
            # Prefer 1st of month
            best = min(month_list, key=lambda b: abs(b["time"].day - 1))
            to_keep.add(best["filename"])

        # Delete backups not in keep list
        deleted = 0
        errors = 0

        for backup in backups:
            if backup["filename"] not in to_keep:
                try:
                    filepath = os.path.join(self.backup_dir, backup["filename"])
                    os.remove(filepath)
                    deleted += 1
                    logger.info(f"Deleted old backup: {backup['filename']}")
                except Exception as e:
                    errors += 1
                    logger.error(f"Failed to delete {backup['filename']}: {e}")

        logger.info(f"Backup cleanup: kept={len(to_keep)}, deleted={deleted}, errors={errors}")

        return {
            "kept": len(to_keep),
            "deleted": deleted,
            "errors": errors
        }

    def get_status(self) -> Dict:
        """
        Get backup system status.

        Returns:
            Dict with status info (enabled, last_backup, count, total_size, interval)
        """
        backups = self.list_backups()
        total_size = sum(b["size"] for b in backups)

        # Get last backup time from backups list or cached value
        last_backup = None
        if backups:
            last_backup = backups[0]["created_at"]
        elif self._last_backup_time:
            last_backup = self._last_backup_time.isoformat()

        return {
            "enabled": settings.backup_enabled,
            "interval_hours": settings.backup_interval_hours,
            "backup_dir": self.backup_dir,
            "last_backup": last_backup,
            "last_error": self._last_backup_error,
            "count": len(backups),
            "total_size": total_size,
            "retention": {
                "hourly_hours": settings.backup_retention_hourly,
                "daily_days": settings.backup_retention_daily,
                "weekly_weeks": settings.backup_retention_weekly,
                "monthly_months": settings.backup_retention_monthly
            }
        }


# Singleton instance
backup_service = BackupService()
