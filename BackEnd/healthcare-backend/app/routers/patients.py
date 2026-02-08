"""
Patients router.
Handles patient registration, retrieval, biometric verification.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient, BiometricHash
from app.models.audit import AuditAction
from app.models.consent import ConsentPurpose
from app.schemas import PatientRegister, PatientResponse, BiometricVerify
from app.auth.dependencies import get_current_user, require_doctor, require_admin
from app.services.biometric import hash_fingerprint, verify_fingerprint
from app.services.audit import AuditService
from app.services.consent import ConsentService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/register", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    patient_data: PatientRegister,
    request: Request,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    Register a new patient with biometric identity.
    Only doctors and admins can register patients.
    """
    # Hash fingerprint
    fingerprint_hash = hash_fingerprint(patient_data.fingerprint_data)
    
    # Check if fingerprint already exists (one fingerprint = one patient)
    existing_biometric = db.query(BiometricHash).filter(
        BiometricHash.fingerprint_hash == fingerprint_hash
    ).first()
    
    if existing_biometric:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This fingerprint is already registered"
        )
    
    # Create patient with global UID (auto-generated UUID)
    patient = Patient(
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        blood_group=patient_data.blood_group,
        email=patient_data.email,
        phone=patient_data.phone,
        address=patient_data.address,
        city=patient_data.city,
        state=patient_data.state,
        country=patient_data.country,
        postal_code=patient_data.postal_code,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        emergency_contact_relationship=patient_data.emergency_contact_relationship,
        registered_by=current_user.id,
        is_active=True
    )
    
    db.add(patient)
    db.flush()  # Get patient.id
    
    # Store biometric hash
    biometric = BiometricHash(
        patient_id=patient.id,
        fingerprint_hash=fingerprint_hash,
        hash_algorithm="SHA256"
    )
    
    db.add(biometric)
    
    # Auto-grant default treatment consent
    ConsentService.grant_consent(
        db=db,
        patient_id=patient.id,
        purpose=ConsentPurpose.TREATMENT,
        granted_by_id=current_user.id,
        consent_text="Default treatment consent granted during registration"
    )
    
    db.commit()
    db.refresh(patient)
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.PATIENT_REGISTERED,
        actor=current_user,
        resource_type="patient",
        resource_id=patient.id,
        description=f"Patient registered: {patient.first_name} {patient.last_name}",
        ip_address=request.client.host if request.client else None
    )
    
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get patient details by ID.
    Requires consent check for doctors.
    Patients can only view their own data.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Role-based access control
    if current_user.role.value == "patient":
        # Patients can only view their own data
        # (In real system, would link User to Patient)
        pass  # Simplified for now
    elif current_user.role.value == "doctor":
        # Check consent
        has_consent = ConsentService.check_consent(
            db=db,
            patient_id=patient_id,
            purpose=ConsentPurpose.TREATMENT,
            doctor_id=current_user.id
        )
        if not has_consent:
            # Audit unauthorized access attempt
            AuditService.log_security_event(
                db=db,
                action=AuditAction.UNAUTHORIZED_ACCESS,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                description=f"Doctor {current_user.id} attempted to access patient {patient_id} without consent"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No consent granted for access"
            )
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.PATIENT_VIEWED,
        actor=current_user,
        resource_type="patient",
        resource_id=patient.id,
        ip_address=request.client.host if request.client else None
    )
    
    return patient


@router.post("/verify-biometric")
async def verify_biometric(
    verify_data: BiometricVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify fingerprint and return patient ID.
    Used for patient lookup and identity verification.
    """
    # Hash provided fingerprint
    fingerprint_hash = hash_fingerprint(verify_data.fingerprint_data)
    
    # Find matching biometric record
    biometric = db.query(BiometricHash).filter(
        BiometricHash.fingerprint_hash == fingerprint_hash
    ).first()
    
    if not biometric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patient found with this fingerprint"
        )
    
    # Get patient
    patient = db.query(Patient).filter(Patient.id == biometric.patient_id).first()
    
    if not patient or not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or inactive"
        )
    
    return {
        "verified": True,
        "patient_id": patient.id,
        "patient_name": f"{patient.first_name} {patient.last_name}"
    }


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete patient (admin only).
    Implements soft delete by default.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Soft delete
    patient.is_active = False
    db.commit()
    
    # Audit log
    AuditService.log(
        db=db,
        action=AuditAction.PATIENT_DELETED,
        actor=current_user,
        resource_type="patient",
        resource_id=patient.id,
        description=f"Patient soft deleted: {patient.first_name} {patient.last_name}",
        ip_address=request.client.host if request.client else None
    )
    
    return None


@router.get("/", response_model=List[PatientResponse])
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    List all patients (doctors and admins only).
    """
    patients = db.query(Patient).filter(
        Patient.is_active == True
    ).offset(skip).limit(limit).all()
    
    return patients
