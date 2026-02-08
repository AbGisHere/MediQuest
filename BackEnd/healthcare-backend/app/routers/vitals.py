"""
Vitals router.
Handles vital signs upload, batch upload, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient
from app.models.vitals import Vital
from app.models.audit import AuditAction
from app.models.consent import ConsentPurpose
from app.schemas import VitalCreate, VitalBatchCreate, VitalResponse
from app.auth.dependencies import get_current_user, require_doctor
from app.services.biometric import generate_checksum
from app.services.audit import AuditService
from app.services.consent import ConsentService
from app.services.alerts import AlertEngine
import uuid

router = APIRouter(prefix="/vitals", tags=["Vitals"])


@router.post("/", response_model=VitalResponse, status_code=status.HTTP_201_CREATED)
async def upload_vital(
    vital_data: VitalCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a single vital measurement.
    Automatically triggers alert evaluation.
    """
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == vital_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check consent (except for emergency)
    if current_user.role.value == "doctor":
        has_consent = ConsentService.check_consent(
            db=db,
            patient_id=vital_data.patient_id,
            purpose=ConsentPurpose.TREATMENT,
            doctor_id=current_user.id
        )
        if not has_consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No consent granted for data upload"
            )
    
    # Create vital record
    vital = Vital(
        patient_id=vital_data.patient_id,
        vital_type=vital_data.vital_type,
        value=vital_data.value,
        unit=vital_data.unit,
        source=vital_data.source,
        source_id=vital_data.source_id or current_user.id,
        recorded_at=vital_data.recorded_at,
        notes=vital_data.notes,
        checksum=vital_data.checksum,
        uploaded_by=current_user.id
    )
    
    db.add(vital)
    db.commit()
    db.refresh(vital)
    
    # Evaluate for alerts
    AlertEngine.evaluate_vital(db, vital)
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.VITAL_UPLOADED,
        actor=current_user,
        resource_type="vital",
        resource_id=vital.id,
        description=f"Vital uploaded: {vital.vital_type}={vital.value}{vital.unit} for patient {vital.patient_id}",
        metadata={"vital_type": vital.vital_type, "value": vital.value},
        ip_address=request.client.host if request.client else None
    )
    
    return vital


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def batch_upload(
    batch_data: VitalBatchCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Batch upload vitals (for offline-first support).
    Validates checksums, detects duplicates, prevents replay attacks.
    """
    batch_id = batch_data.batch_id or str(uuid.uuid4())
    uploaded_vitals = []
    skipped_vitals = []
    errors = []
    
    for vital_data in batch_data.vitals:
        try:
            # Check if patient exists
            patient = db.query(Patient).filter(Patient.id == vital_data.patient_id).first()
            if not patient:
                errors.append({
                    "vital": vital_data.dict(),
                    "error": "Patient not found"
                })
                continue
            
            # Validate checksum if provided
            if vital_data.checksum:
                # Create canonical data string for validation
                data_str = f"{vital_data.patient_id}{vital_data.vital_type}{vital_data.value}{vital_data.recorded_at.isoformat()}"
                expected_checksum = generate_checksum(data_str)
                
                if vital_data.checksum != expected_checksum:
                    errors.append({
                        "vital": vital_data.dict(),
                        "error": "Invalid checksum"
                    })
                    continue
            
            # Check for duplicates (same patient, type, value, recorded_at)
            duplicate = db.query(Vital).filter(
                Vital.patient_id == vital_data.patient_id,
                Vital.vital_type == vital_data.vital_type,
                Vital.recorded_at == vital_data.recorded_at,
                Vital.value == vital_data.value
            ).first()
            
            if duplicate:
                skipped_vitals.append({
                    "vital": vital_data.dict(),
                    "reason": "Duplicate detected"
                })
                continue
            
            # Create vital record
            vital = Vital(
                patient_id=vital_data.patient_id,
                vital_type=vital_data.vital_type,
                value=vital_data.value,
                unit=vital_data.unit,
                source=vital_data.source,
                source_id=vital_data.source_id or current_user.id,
                recorded_at=vital_data.recorded_at,
                notes=vital_data.notes,
                checksum=vital_data.checksum,
                batch_id=batch_id,
                uploaded_by=current_user.id
            )
            
            db.add(vital)
            uploaded_vitals.append(vital)
            
        except Exception as e:
            errors.append({
                "vital": vital_data.dict(),
                "error": str(e)
            })
    
    # Commit all valid vitals
    db.commit()
    
    # Evaluate alerts for all uploaded vitals
    alerts = AlertEngine.evaluate_batch(db, uploaded_vitals)
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.BATCH_UPLOAD,
        actor=current_user,
        resource_type="batch",
        resource_id=batch_id,
        description=f"Batch upload completed: {len(uploaded_vitals)} uploaded, {len(skipped_vitals)} skipped, {len(errors)} errors",
        metadata={
            "batch_id": batch_id,
            "uploaded_count": len(uploaded_vitals),
            "skipped_count": len(skipped_vitals),
            "error_count": len(errors),
            "alerts_generated": len(alerts)
        },
        ip_address=request.client.host if request.client else None
    )
    
    return {
        "batch_id": batch_id,
        "uploaded_count": len(uploaded_vitals),
        "skipped_count": len(skipped_vitals),
        "error_count": len(errors),
        "alerts_generated": len(alerts),
        "uploaded_vitals": [{"id": v.id, "vital_type": v.vital_type} for v in uploaded_vitals],
        "skipped_vitals": skipped_vitals,
        "errors": errors
    }


@router.get("/{patient_id}", response_model=List[VitalResponse])
async def get_patient_vitals(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    vital_type: str = None,
    limit: int = 100
):
    """
    Get vitals for a patient.
    Supports filtering by vital type.
    Returns most recent vitals first.
    """
    # Check if patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check consent
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
                detail="No consent granted for data access"
            )
    
    # Query vitals
    query = db.query(Vital).filter(Vital.patient_id == patient_id)
    
    if vital_type:
        query = query.filter(Vital.vital_type == vital_type)
    
    vitals = query.order_by(Vital.recorded_at.desc()).limit(limit).all()
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.VITAL_VIEWED,
        actor=current_user,
        resource_type="vital",
        resource_id=patient_id,
        description=f"Vitals viewed for patient {patient_id}",
        metadata={"vital_type": vital_type, "count": len(vitals)},
        ip_address=request.client.host if request.client else None
    )
    
    return vitals
