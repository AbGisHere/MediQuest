"""
Health profile router.
Provides unified health profile aggregation (DigiLocker equivalent).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import Vital
from app.models.alert import Alert
from app.models.audit import HealthCondition, Allergy, AuditAction
from app.models.consent import ConsentPurpose
from app.schemas import PatientResponse, VitalResponse, AlertResponse, HealthConditionCreate, AllergyCreate
from app.auth.dependencies import get_current_user
from app.services.consent import ConsentService
from app.services.audit import AuditService

router = APIRouter(prefix="/health-profile", tags=["Health Profile"])


@router.get("/{patient_id}")
async def get_unified_health_profile(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get unified health profile for a patient.
    This is the DigiLocker equivalent - single source of truth.
    
    Returns:
    - Patient demographics
    - Chronic conditions
    - Allergies
    - Recent vitals (last 30 days)
    - Recent alerts
    - Last updated timestamp
    """
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check consent (unless admin)
    if current_user.role.value == "doctor":
        has_consent = ConsentService.check_consent(
            db=db,
            patient_id=patient_id,
            purpose=ConsentPurpose.TREATMENT,
            doctor_id=current_user.id
        )
        if not has_consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No consent granted for access"
            )
    
    # Get health conditions
    conditions = db.query(HealthCondition).filter(
        HealthCondition.patient_id == patient_id,
        HealthCondition.is_active == True
    ).all()
    
    # Get allergies
    allergies = db.query(Allergy).filter(
        Allergy.patient_id == patient_id,
        Allergy.is_active == True
    ).all()
    
    # Get recent vitals (last 20)
    recent_vitals = db.query(Vital).filter(
        Vital.patient_id == patient_id
    ).order_by(Vital.recorded_at.desc()).limit(20).all()
    
    # Get recent alerts (last 10 unresolved)
    recent_alerts = db.query(Alert).filter(
        Alert.patient_id == patient_id,
        Alert.resolved == False
    ).order_by(Alert.created_at.desc()).limit(10).all()
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.PATIENT_VIEWED,
        actor=current_user,
        resource_type="health_profile",
        resource_id=patient_id,
        description=f"Health profile viewed for patient {patient_id}",
        ip_address=request.client.host if request.client else None
    )
    
    # Construct unified profile
    profile = {
        "patient": PatientResponse.from_orm(patient),
        "chronic_conditions": [
            {
                "id": c.id,
                "condition_name": c.condition_name,
                "severity": c.severity,
                "diagnosed_date": c.diagnosed_date,
                "notes": c.notes
            } for c in conditions
        ],
        "allergies": [
            {
                "id": a.id,
                "allergen": a.allergen,
                "reaction": a.reaction,
                "severity": a.severity,
                "diagnosed_date": a.diagnosed_date
            } for a in allergies
        ],
        "recent_vitals": [VitalResponse.from_orm(v) for v in recent_vitals],
        "recent_alerts": [AlertResponse.from_orm(a) for a in recent_alerts],
        "last_updated": datetime.now(timezone.utc),
        "profile_completeness": {
            "demographics": True,
            "conditions": len(conditions) > 0,
            "allergies": len(allergies) > 0,
            "vitals": len(recent_vitals) > 0
        }
    }
    
    return profile


@router.post("/conditions", status_code=status.HTTP_201_CREATED)
async def add_health_condition(
    condition_data: HealthConditionCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a chronic health condition for a patient.
    Only doctors can add conditions.
    """
    if current_user.role.value not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can add health conditions"
        )
    
    # Check consent
    has_consent = ConsentService.check_consent(
        db=db,
        patient_id=condition_data.patient_id,
        purpose=ConsentPurpose.TREATMENT,
        doctor_id=current_user.id
    )
    if not has_consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No consent granted"
        )
    
    condition = HealthCondition(
        patient_id=condition_data.patient_id,
        condition_name=condition_data.condition_name,
        diagnosed_date=condition_data.diagnosed_date,
        diagnosed_by=current_user.id,
        severity=condition_data.severity,
        notes=condition_data.notes,
        is_active=True
    )
    
    db.add(condition)
    db.commit()
    db.refresh(condition)
    
    return condition


@router.post("/allergies", status_code=status.HTTP_201_CREATED)
async def add_allergy(
    allergy_data: AllergyCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an allergy for a patient.
    Only doctors can add allergies.
    """
    if current_user.role.value not in ["doctor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can add allergies"
        )
    
    # Check consent
    has_consent = ConsentService.check_consent(
        db=db,
        patient_id=allergy_data.patient_id,
        purpose=ConsentPurpose.TREATMENT,
        doctor_id=current_user.id
    )
    if not has_consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No consent granted"
        )
    
    allergy = Allergy(
        patient_id=allergy_data.patient_id,
        allergen=allergy_data.allergen,
        reaction=allergy_data.reaction,
        diagnosed_date=allergy_data.diagnosed_date,
        diagnosed_by=current_user.id,
        severity=allergy_data.severity,
        is_active=True
    )
    
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    
    return allergy
