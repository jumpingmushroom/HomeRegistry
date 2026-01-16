from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import qrcode
from io import BytesIO

from ..database import get_db
from ..models.item import Item, ItemCondition
from ..models.user import User
from ..services.auth_service import get_current_user

router = APIRouter(tags=["public"])


class PublicItemResponse(BaseModel):
    """Limited item data for public view (no auth required)"""
    id: str
    name: str
    description: Optional[str] = None
    category_name: Optional[str] = None
    condition: Optional[ItemCondition] = None
    primary_image_id: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/api/public/items/{item_id}", response_model=PublicItemResponse)
async def get_public_item(item_id: str, db: Session = Depends(get_db)):
    """
    Get limited item information for public view.
    No authentication required.
    Shows: name, description, category, condition, primary image.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Find primary image
    primary_image_id = None
    for img in item.images:
        if img.is_primary:
            primary_image_id = img.id
            break
    # Fallback to first image if no primary set
    if not primary_image_id and item.images:
        primary_image_id = item.images[0].id

    return PublicItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        category_name=item.category.name if item.category else None,
        condition=item.condition,
        primary_image_id=primary_image_id
    )


@router.get("/api/items/{item_id}/qr")
async def get_item_qr_code(
    item_id: str,
    base_url: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Generate a QR code for an item.
    The QR code links to the public item view.
    No auth required - item IDs are UUIDs obtained from authenticated endpoints.

    Query params:
    - base_url: Override the base URL for the QR code link (e.g., https://yourdomain.com)
    """
    # Verify item exists
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Build the URL for the QR code
    # Default to a relative path if no base_url provided
    if base_url:
        # Remove trailing slash if present
        base_url = base_url.rstrip('/')
        qr_url = f"{base_url}/public/items/{item_id}"
    else:
        # Use relative path - frontend will need to handle this
        qr_url = f"/public/items/{item_id}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return Response(
        content=img_bytes.getvalue(),
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename=qr_{item_id}.png"
        }
    )
