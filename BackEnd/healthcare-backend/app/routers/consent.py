"""
Consent management router.
Handles consent granting, revocation, and status checking.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.consent import Consent, ConsentPurpose
from app.models.audit import AuditAction
from app.schemas import ConsentGrant, ConsentRevoke, ConsentResponse
from app.auth.dependencies import get_current_user
from app.services.consent import ConsentService
from app.services.audit import AuditService

router = APIRouter(prefix="/consent", tags=["Consent"])


@router.post("/grant", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def grant_consent(
    consent_data: ConsentGrant,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Grant consent for a specific purpose.
    Patient or authorized users can grant consent.
    """
    # In a real system, verify that current_user has authority to grant
    # For now, allow any authenticated user
    
    consent = ConsentService.grant_consent(
        db=db,
        patient_id=consent_data.patient_id,
        purpose=consent_data.purpose,
        granted_by_id=current_user.id,
        granted_to_id=consent_data.granted_to_id,
        consent_text=consent_data.consent_text,
        expiry_date=consent_data.expiry_date
    )
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.CONSENT_GRANTED,
        actor=current_user,
        resource_type="consent",
        resource_id=consent.id,
        description=f"Consent granted for patient {consent_data.patient_id}, purpose: {consent_data.purpose}",
        metadata={"purpose": consent_data.purpose.value, "patient_id": consent_data.patient_id},
        ip_address=request.client.host if request.client else None
    )
    
    return consent


@router.post("/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_data: ConsentRevoke,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke previously granted consent.
    This blocks future access to patient data for the specified purpose.
    """
    consent = ConsentService.revoke_consent(
        db=db,
        patient_id=consent_data.patient_id,
        purpose=consent_data.purpose,
        revoked_by_id=current_user.id,
        granted_to_id=consent_data.granted_to_id
    )
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active consent found to revoke"
        )
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.CONSENT_REVOKED,
        actor=current_user,
        resource_type="consent",
        resource_id=consent.id,
        description=f"Consent revoked for patient {consent_data.patient_id}, purpose: {consent_data.purpose}",
        metadata={"purpose": consent_data.purpose.value, "patient_id": consent_data.patient_id},
        ip_address=request.client.host if request.client else None
    )
    
    return consent


@router.get("/{patient_id}", response_model=List[ConsentResponse])
async def get_patient_consents(
    patient_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all consent records for a patient.
    Shows both active and revoked consents.
    """
    consents = db.query(Consent).filter(
        Consent.patient_id == patient_id
    ).order_by(Consent.created_at.desc()).all()
    
    return consents


@router.get("/{patient_id}/check/{purpose}")
async def check_consent(
    patient_id: str,
    purpose: ConsentPurpose,
    doctor_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if consent is granted for a specific purpose.
    Returns boolean status.
    """
    has_consent = ConsentService.check_consent(
        db=db,
        patient_id=patient_id,
        purpose=purpose,
        doctor_id=doctor_id
    )
    
    return {
        "patient_id": patient_id,
        "purpose": purpose.value,
        "doctor_id": doctor_id,
        "has_consent": has_consent
    }
