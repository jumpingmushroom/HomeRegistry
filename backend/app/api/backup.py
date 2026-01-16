"""
Backup API endpoints.
"""
import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..models.user import User
from ..services.auth_service import get_current_user
from ..services.backup_service import backup_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.post("/create")
async def create_backup(current_user: User = Depends(get_current_user)):
    """
    Manually trigger a database backup.

    Returns backup metadata on success.
    """
    logger.info(f"Manual backup triggered by user: {current_user.id}")

    try:
        result = backup_service.create_backup()
        return {
            "success": True,
            "message": "Backup created successfully",
            "backup": result
        }
    except FileNotFoundError as e:
        logger.error(f"Backup failed - database not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database not found: {e}"
        )
    except IOError as e:
        logger.error(f"Backup failed - IO error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backup failed: {e}"
        )


@router.get("/list")
async def list_backups(current_user: User = Depends(get_current_user)):
    """
    List all available backups with metadata.
    """
    logger.info(f"Backup list requested by user: {current_user.id}")

    backups = backup_service.list_backups()
    return {
        "backups": backups,
        "count": len(backups)
    }


@router.get("/download/{filename}")
async def download_backup(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a specific backup file.

    Validates filename to prevent path traversal attacks.
    """
    logger.info(f"Backup download requested by user {current_user.id}: {filename}")

    # Security validation and path resolution
    filepath = backup_service.get_backup_path(filename)

    if filepath is None:
        logger.warning(f"Invalid backup request from user {current_user.id}: {filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup not found or invalid filename"
        )

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/x-sqlite3"
    )


@router.get("/download-current")
async def download_current_database(current_user: User = Depends(get_current_user)):
    """
    Download the current live database with timestamp in filename.
    """
    logger.info(f"Current database download requested by user: {current_user.id}")

    db_path = backup_service.get_current_db_path()

    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database file not found"
        )

    # Generate timestamped filename for download
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_filename = f"homeregistry_current_{timestamp}.db"

    return FileResponse(
        path=db_path,
        filename=download_filename,
        media_type="application/x-sqlite3"
    )


@router.delete("/cleanup")
async def trigger_cleanup(current_user: User = Depends(get_current_user)):
    """
    Manually trigger backup retention cleanup.
    """
    logger.info(f"Manual cleanup triggered by user: {current_user.id}")

    result = backup_service.cleanup_old_backups()

    return {
        "success": True,
        "message": "Cleanup completed",
        "result": result
    }


@router.get("/status")
async def get_backup_status(current_user: User = Depends(get_current_user)):
    """
    Get backup system status.

    Returns enabled state, last backup time, backup count, total size, etc.
    """
    logger.info(f"Backup status requested by user: {current_user.id}")

    status_info = backup_service.get_status()
    return status_info
