from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.property import Property
from ..models.insurance_policy import InsurancePolicy
from ..models.item import Item
from ..models.location import Location
from ..services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/insurance/{property_id}")
async def generate_insurance_report(property_id: str, db: Session = Depends(get_db)):
    """Generate an insurance inventory report PDF for a property."""

    # Fetch property
    property = db.query(Property).filter(Property.id == property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    # Fetch insurance policies for property
    policies = db.query(InsurancePolicy).filter(
        InsurancePolicy.property_id == property_id
    ).all()

    # Fetch all items for property with eager loading
    items = db.query(Item).filter(
        Item.property_id == property_id
    ).all()

    # Fetch locations for property
    locations = db.query(Location).filter(
        Location.property_id == property_id
    ).all()

    # Generate report
    report_service = ReportService()
    pdf_bytes = report_service.generate_insurance_report(
        property=property,
        policies=policies,
        items=items,
        locations=locations
    )

    # Generate filename
    safe_name = property.name.replace(" ", "_").replace("/", "-")
    filename = f"insurance_report_{safe_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
