from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.image import Image
from ..models.user import User
from ..services.auth_service import get_current_user
from ..schemas.image import ImageResponse
from ..services.image_service import ImageService

router = APIRouter(prefix="/api/images", tags=["images"])


@router.delete("/{image_id}")
async def delete_image(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an image"""
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file
    image_service = ImageService()
    thumbnail_filename = f"{db_image.filename.rsplit('.', 1)[0]}.webp"
    await image_service.delete_image(db_image.filename, thumbnail_filename)

    # Delete database record
    db.delete(db_image)
    db.commit()

    return {"message": "Image deleted successfully"}


@router.put("/{image_id}/primary", response_model=ImageResponse)
async def set_primary_image(image_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Set an image as primary for its item"""
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Unset all other images as primary for this item
    db.query(Image).filter(
        Image.item_id == db_image.item_id,
        Image.id != image_id
    ).update({"is_primary": False})

    # Set this image as primary
    db_image.is_primary = True
    db.commit()
    db.refresh(db_image)

    return ImageResponse.model_validate(db_image)


@router.get("/{image_id}/file")
async def get_image_file(image_id: str, thumbnail: bool = False, db: Session = Depends(get_db)):
    """Get image file. No auth required - image IDs are UUIDs obtained from authenticated endpoints."""
    db_image = db.query(Image).filter(Image.id == image_id).first()
    if not db_image:
        raise HTTPException(status_code=404, detail="Image not found")

    image_service = ImageService()

    if thumbnail:
        thumbnail_filename = f"{db_image.filename.rsplit('.', 1)[0]}.webp"
        filepath = image_service.get_thumbnail_path(thumbnail_filename)
    else:
        filepath = image_service.get_image_path(db_image.filename)

    return FileResponse(filepath)
