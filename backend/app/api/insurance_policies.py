from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.insurance_policy import InsurancePolicy
from ..models.property import Property
from ..models.user import User
from ..services.auth_service import get_current_user
from ..schemas.insurance_policy import InsurancePolicyCreate, InsurancePolicyUpdate, InsurancePolicyResponse

router = APIRouter(prefix="/api/insurance-policies", tags=["insurance-policies"])


@router.get("", response_model=List[InsurancePolicyResponse])
async def get_insurance_policies(
    property_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all insurance policies, optionally filtered by property"""
    query = db.query(InsurancePolicy)
    if property_id:
        query = query.filter(InsurancePolicy.property_id == property_id)

    policies = query.all()
    result = []
    for policy in policies:
        response = InsurancePolicyResponse(
            id=policy.id,
            property_id=policy.property_id,
            name=policy.name,
            company_name=policy.company_name,
            policy_number=policy.policy_number,
            policy_type=policy.policy_type,
            coverage_amount=policy.coverage_amount,
            deductible=policy.deductible,
            premium=policy.premium,
            currency=policy.currency,
            start_date=policy.start_date,
            renewal_date=policy.renewal_date,
            agent_name=policy.agent_name,
            agent_phone=policy.agent_phone,
            agent_email=policy.agent_email,
            notes=policy.notes,
            created_at=policy.created_at,
            updated_at=policy.updated_at,
            property_name=policy.property.name if policy.property else None
        )
        result.append(response)
    return result


@router.get("/{policy_id}", response_model=InsurancePolicyResponse)
async def get_insurance_policy(policy_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get a single insurance policy"""
    policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not policy:
        raise HTTPException(status_code=404, detail="Insurance policy not found")

    return InsurancePolicyResponse(
        id=policy.id,
        property_id=policy.property_id,
        name=policy.name,
        company_name=policy.company_name,
        policy_number=policy.policy_number,
        policy_type=policy.policy_type,
        coverage_amount=policy.coverage_amount,
        deductible=policy.deductible,
        premium=policy.premium,
        currency=policy.currency,
        start_date=policy.start_date,
        renewal_date=policy.renewal_date,
        agent_name=policy.agent_name,
        agent_phone=policy.agent_phone,
        agent_email=policy.agent_email,
        notes=policy.notes,
        created_at=policy.created_at,
        updated_at=policy.updated_at,
        property_name=policy.property.name if policy.property else None
    )


@router.post("", response_model=InsurancePolicyResponse)
async def create_insurance_policy(policy: InsurancePolicyCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new insurance policy"""
    # Validate property exists
    property = db.query(Property).filter(Property.id == policy.property_id).first()
    if not property:
        raise HTTPException(status_code=404, detail="Property not found")

    db_policy = InsurancePolicy(**policy.model_dump())
    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)

    return InsurancePolicyResponse(
        id=db_policy.id,
        property_id=db_policy.property_id,
        name=db_policy.name,
        company_name=db_policy.company_name,
        policy_number=db_policy.policy_number,
        policy_type=db_policy.policy_type,
        coverage_amount=db_policy.coverage_amount,
        deductible=db_policy.deductible,
        premium=db_policy.premium,
        currency=db_policy.currency,
        start_date=db_policy.start_date,
        renewal_date=db_policy.renewal_date,
        agent_name=db_policy.agent_name,
        agent_phone=db_policy.agent_phone,
        agent_email=db_policy.agent_email,
        notes=db_policy.notes,
        created_at=db_policy.created_at,
        updated_at=db_policy.updated_at,
        property_name=property.name
    )


@router.put("/{policy_id}", response_model=InsurancePolicyResponse)
async def update_insurance_policy(
    policy_id: str,
    policy: InsurancePolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an insurance policy"""
    db_policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Insurance policy not found")

    for field, value in policy.model_dump(exclude_unset=True).items():
        setattr(db_policy, field, value)

    db.commit()
    db.refresh(db_policy)

    return InsurancePolicyResponse(
        id=db_policy.id,
        property_id=db_policy.property_id,
        name=db_policy.name,
        company_name=db_policy.company_name,
        policy_number=db_policy.policy_number,
        policy_type=db_policy.policy_type,
        coverage_amount=db_policy.coverage_amount,
        deductible=db_policy.deductible,
        premium=db_policy.premium,
        currency=db_policy.currency,
        start_date=db_policy.start_date,
        renewal_date=db_policy.renewal_date,
        agent_name=db_policy.agent_name,
        agent_phone=db_policy.agent_phone,
        agent_email=db_policy.agent_email,
        notes=db_policy.notes,
        created_at=db_policy.created_at,
        updated_at=db_policy.updated_at,
        property_name=db_policy.property.name if db_policy.property else None
    )


@router.delete("/{policy_id}")
async def delete_insurance_policy(policy_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an insurance policy"""
    db_policy = db.query(InsurancePolicy).filter(InsurancePolicy.id == policy_id).first()
    if not db_policy:
        raise HTTPException(status_code=404, detail="Insurance policy not found")

    db.delete(db_policy)
    db.commit()
    return {"message": "Insurance policy deleted successfully"}
