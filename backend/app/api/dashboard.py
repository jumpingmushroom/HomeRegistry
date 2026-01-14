from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..database import get_db
from ..models.item import Item
from ..models.category import Category
from ..models.location import Location

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics, optionally filtered by property"""
    # Base query filters
    item_filter = Item.property_id == property_id if property_id else True
    location_filter = Location.property_id == property_id if property_id else True

    # Total items
    total_items = db.query(func.count(Item.id)).filter(item_filter).scalar()

    # Total inventory value
    total_value = db.query(func.sum(Item.current_value)).filter(item_filter).scalar() or 0

    # Items by category
    items_by_category_query = db.query(
        Category.name,
        func.count(Item.id).label("count")
    ).join(Item, Category.id == Item.category_id, isouter=True)

    if property_id:
        items_by_category_query = items_by_category_query.filter(Item.property_id == property_id)

    items_by_category = items_by_category_query.group_by(Category.name).all()

    category_data = [{"name": name or "Uncategorized", "count": count} for name, count in items_by_category]

    # Items by location
    items_by_location_query = db.query(
        Location.name,
        func.count(Item.id).label("count")
    ).join(Item, Location.id == Item.location_id, isouter=True)

    if property_id:
        items_by_location_query = items_by_location_query.filter(Location.property_id == property_id)

    items_by_location = items_by_location_query.group_by(Location.name).all()

    location_data = [{"name": name or "No Location", "count": count} for name, count in items_by_location]

    # Recently added items (last 10)
    recent_items_query = db.query(Item)
    if property_id:
        recent_items_query = recent_items_query.filter(Item.property_id == property_id)

    recent_items = recent_items_query\
        .order_by(Item.created_at.desc())\
        .limit(10)\
        .all()

    recent_items_data = [{
        "id": item.id,
        "name": item.name,
        "created_at": item.created_at.isoformat(),
        "category": item.category.name if item.category else None,
        "location": item.location.name if item.location else None
    } for item in recent_items]

    # Expiring warranties (next 30 days)
    today = datetime.now().date()
    thirty_days = today + timedelta(days=30)

    expiring_warranties_query = db.query(Item)\
        .filter(Item.warranty_expiration.isnot(None))\
        .filter(Item.warranty_expiration >= today)\
        .filter(Item.warranty_expiration <= thirty_days)

    if property_id:
        expiring_warranties_query = expiring_warranties_query.filter(Item.property_id == property_id)

    expiring_warranties = expiring_warranties_query\
        .order_by(Item.warranty_expiration)\
        .all()

    warranty_data = [{
        "id": item.id,
        "name": item.name,
        "warranty_expiration": item.warranty_expiration.isoformat(),
        "days_remaining": (item.warranty_expiration - today).days
    } for item in expiring_warranties]

    return {
        "total_items": total_items,
        "total_value": float(total_value),
        "items_by_category": category_data,
        "items_by_location": location_data,
        "recent_items": recent_items_data,
        "expiring_warranties": warranty_data
    }
