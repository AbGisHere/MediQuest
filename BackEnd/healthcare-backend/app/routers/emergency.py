"""
Emergency access router.
Handles emergency/crash scenarios with time-limited consent bypass.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.emergency import EmergencyAccess
from app.models.audit import AuditAction
from app.schemas import EmergencyTrigger, EmergencyAccessResponse, HealthProfileResponse, PatientResponse
from app.auth.dependencies import get_current_user
from app.services.audit import AuditService
from app.config import settings

router = APIRouter(prefix="/emergency", tags=["Emergency"])


@router.post("/trigger", response_model=EmergencyAccessResponse, status_code=status.HTTP_201_CREATED)
async def trigger_emergency_access(
    emergency_data: EmergencyTrigger,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger emergency access for a patient.
    Bypasses consent with full audit logging.
    Auto-expires after configured duration.
    """
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == emergency_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Calculate expiry time
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMERGENCY_ACCESS_DURATION_HOURS
    )
    
    # Create emergency access record
    emergency_access = EmergencyAccess(
        patient_id=emergency_data.patient_id,
        triggered_by=current_user.id,
        trigger_reason=emergency_data.trigger_reason,
        trigger_keyword=emergency_data.trigger_keyword,
        expires_at=expires_at,
        is_active=True,
        hospital_notified=False  # Mock notification (implement actual notification)
    )
    
    db.add(emergency_access)
    db.commit()
    db.refresh(emergency_access)
    
    # Mock hospital notification
    # In production, this would send actual notification
    emergency_access.hospital_notified = True
    emergency_access.notification_sent_at = datetime.now(timezone.utc)
    db.commit()
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.EMERGENCY_TRIGGERED,
        actor=current_user,
        resource_type="emergency_access",
        resource_id=emergency_access.id,
        description=f"Emergency access triggered for patient {emergency_data.patient_id}. Reason: {emergency_data.trigger_reason}",
        metadata={
            "patient_id": emergency_data.patient_id,
            "trigger_keyword": emergency_data.trigger_keyword,
            "expires_at": expires_at.isoformat()
        },
        ip_address=request.client.host if request.client else None
    )
    
    return emergency_access


@router.get("/access/{patient_id}")
async def emergency_access_data(
    patient_id: str,
    emergency_access_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Access patient data in emergency mode.
    Requires valid emergency access record.
    Read-only access, fully audited.
    """
    # Verify emergency access
    emergency_access = db.query(EmergencyAccess).filter(
        EmergencyAccess.id == emergency_access_id,
        EmergencyAccess.patient_id == patient_id
    ).first()
    
    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency access not found"
        )
    
    # Check if access is still valid
    if emergency_access.has_expired:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Emergency access has expired"
        )
    
    if emergency_access.terminated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Emergency access has been terminated"
        )
    
    # Update access tracking
    emergency_access.access_count += 1
    emergency_access.last_accessed_at = datetime.now(timezone.utc)
    db.commit()
    
    # Get patient data
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.EMERGENCY_ACCESS,
        actor=current_user,
        resource_type="patient",
        resource_id=patient_id,
        description=f"Emergency access to patient {patient_id} data",
        metadata={
            "emergency_access_id": emergency_access_id,
            "access_count": emergency_access.access_count
        },
        ip_address=request.client.host if request.client else None
    )
    
    # Return patient data (simplified - in production return full health profile)
    return {
        "emergency_access_id": emergency_access_id,
        "patient": PatientResponse.from_orm(patient),
        "access_granted_at": emergency_access.granted_at,
        "access_expires_at": emergency_access.expires_at,
        "access_count": emergency_access.access_count,
        "warning": "Emergency access - all actions are fully audited"
    }


@router.get("/active")
async def get_active_emergency_access(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all active emergency access records.
    """
    active_accesses = db.query(EmergencyAccess).filter(
        EmergencyAccess.is_active == True
    ).all()
    
    return [
        {
            "id": access.id,
            "patient_id": access.patient_id,
            "triggered_by": access.triggered_by,
            "trigger_reason": access.trigger_reason,
            "granted_at": access.granted_at,
            "expires_at": access.expires_at,
            "access_count": access.access_count
        }
        for access in active_accesses
    ]


@router.post("/terminate/{emergency_access_id}")
async def terminate_emergency_access(
    emergency_access_id: str,
    termination_reason: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually terminate emergency access before expiry.
    """
    emergency_access = db.query(EmergencyAccess).filter(
        EmergencyAccess.id == emergency_access_id
    ).first()
    
    if not emergency_access:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency access not found"
        )
    
    if emergency_access.terminated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emergency access already terminated"
        )
    
    # Terminate access
    emergency_access.terminated = True
    emergency_access.terminated_at = datetime.now(timezone.utc)
    emergency_access.terminated_by = current_user.id
    emergency_access.termination_reason = termination_reason
    emergency_access.is_active = False
    db.commit()
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.EMERGENCY_TERMINATED,
        actor=current_user,
        resource_type="emergency_access",
        resource_id=emergency_access_id,
        description=f"Emergency access terminated. Reason: {termination_reason}",
        metadata={"termination_reason": termination_reason},
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "message": "Emergency access terminated",
        "emergency_access_id": emergency_access_id,
        "terminated_at": emergency_access.terminated_at
    }
