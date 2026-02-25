from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from ..database import get_db
from ..models.item import Item
from ..models.category import Category
from ..models.location import Location
from ..models.property import Property
from ..models.insurance_policy import InsurancePolicy
from ..models.image import Image
from ..models.document import Document
from ..models.user import User
from ..services.auth_service import get_current_user
from .settings import get_setting_value

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics, optionally filtered by property"""
    # Base query filters
    item_filter = Item.property_id == property_id if property_id else True
    location_filter = Location.property_id == property_id if property_id else True

    # Get high value threshold from settings
    high_value_threshold = get_setting_value(db, "high_value_threshold", 5000)

    # Combined query for total items and total value
    stats = db.query(
        func.count(Item.id),
        func.sum(Item.current_value)
    ).filter(item_filter).first()
    
    total_items = stats[0] or 0
    total_value = stats[1] or 0

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

    # ============== COVERAGE GAPS ==============

    # Get all item IDs that have documents
    items_with_docs_subquery = db.query(Document.item_id).distinct()
    # Get all item IDs that have images
    items_with_images_subquery = db.query(Image.item_id).distinct()

    # Items without documents
    no_docs_query = db.query(Item).filter(item_filter).filter(
        ~Item.id.in_(items_with_docs_subquery)
    )
    no_documents_count = no_docs_query.count()
    no_documents_ids = [row[0] for row in no_docs_query.with_entities(Item.id).limit(50).all()]

    # Items without images
    no_images_query = db.query(Item).filter(item_filter).filter(
        ~Item.id.in_(items_with_images_subquery)
    )
    no_images_count = no_images_query.count()
    no_images_ids = [row[0] for row in no_images_query.with_entities(Item.id).limit(50).all()]

    # High-value items without documentation
    high_value_undoc_query = db.query(Item).filter(item_filter).filter(
        Item.current_value >= high_value_threshold,
        ~Item.id.in_(items_with_docs_subquery)
    )
    high_value_undoc_count = high_value_undoc_query.count()
    high_value_undoc_ids = [row[0] for row in high_value_undoc_query.with_entities(Item.id).limit(50).all()]

    # Items missing purchase info (no price OR no date)
    no_purchase_query = db.query(Item).filter(item_filter).filter(
        or_(
            Item.purchase_price.is_(None),
            Item.purchase_date.is_(None)
        )
    )
    no_purchase_count = no_purchase_query.count()
    no_purchase_ids = [row[0] for row in no_purchase_query.with_entities(Item.id).limit(50).all()]

    # Documentation score (% of items that have both images AND documents)
    items_fully_documented = db.query(Item).filter(item_filter).filter(
        Item.id.in_(items_with_docs_subquery),
        Item.id.in_(items_with_images_subquery)
    ).count()

    doc_score = round((items_fully_documented / total_items * 100) if total_items > 0 else 0)

    coverage_gaps = {
        "no_documents": {
            "count": no_documents_count,
            "item_ids": no_documents_ids[:50]  # Limit to first 50 for performance
        },
        "no_images": {
            "count": no_images_count,
            "item_ids": no_images_ids[:50]
        },
        "high_value_undocumented": {
            "count": high_value_undoc_count,
            "item_ids": high_value_undoc_ids[:50],
            "threshold": high_value_threshold
        },
        "no_purchase_info": {
            "count": no_purchase_count,
            "item_ids": no_purchase_ids[:50]
        },
        "documentation_score": doc_score
    }

    # ============== INSURANCE COVERAGE ANALYSIS ==============

    # Pre-calculate inventory values per property
    prop_values_query = db.query(
        Item.property_id,
        func.sum(Item.current_value).label("total_value")
    ).filter(Item.property_id.isnot(None))
    
    if property_id:
        prop_values_query = prop_values_query.filter(Item.property_id == property_id)
        
    prop_values = {row[0]: float(row[1] or 0) for row in prop_values_query.group_by(Item.property_id).all()}

    # Pre-calculate insurance coverage per property
    prop_coverage_query = db.query(
        InsurancePolicy.property_id,
        func.sum(InsurancePolicy.coverage_amount).label("total_coverage")
    ).filter(InsurancePolicy.property_id.isnot(None))
    
    if property_id:
        prop_coverage_query = prop_coverage_query.filter(InsurancePolicy.property_id == property_id)
        
    prop_coverages = {row[0]: float(row[1] or 0) for row in prop_coverage_query.group_by(InsurancePolicy.property_id).all()}

    # Get properties
    if property_id:
        properties = db.query(Property).filter(Property.id == property_id).all()
    else:
        properties = db.query(Property).all()

    total_policy_coverage = 0
    per_property_analysis = []

    for prop in properties:
        prop_item_value = prop_values.get(prop.id, 0.0)
        prop_coverage = prop_coverages.get(prop.id, 0.0)
        total_policy_coverage += prop_coverage

        # Determine status
        if prop_item_value == 0:
            status = "no_items"
        elif prop_coverage >= prop_item_value:
            status = "covered"
        elif prop_coverage >= prop_item_value * 0.8:
            status = "warning"  # Within 80%
        else:
            status = "under_insured"

        per_property_analysis.append({
            "property_id": prop.id,
            "property_name": prop.name,
            "inventory_value": prop_item_value,
            "policy_coverage": prop_coverage,
            "gap": prop_coverage - prop_item_value,
            "status": status
        })

    # Overall coverage ratio
    coverage_ratio = round((total_policy_coverage / float(total_value) * 100) if total_value > 0 else 0)

    insurance_analysis = {
        "total_inventory_value": float(total_value),
        "total_policy_coverage": total_policy_coverage,
        "coverage_ratio": coverage_ratio,
        "coverage_gap": total_policy_coverage - float(total_value),
        "per_property": per_property_analysis
    }

    return {
        "total_items": total_items,
        "total_value": float(total_value),
        "items_by_category": category_data,
        "items_by_location": location_data,
        "recent_items": recent_items_data,
        "expiring_warranties": warranty_data,
        "coverage_gaps": coverage_gaps,
        "insurance_analysis": insurance_analysis,
        "high_value_threshold": high_value_threshold
    }
