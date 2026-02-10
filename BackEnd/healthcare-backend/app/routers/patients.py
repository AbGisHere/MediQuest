"""
Patients router.
Handles patient registration, retrieval, biometric verification (fingerprint + face).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient, BiometricHash, BiometricType
from app.models.audit import AuditAction
from app.models.consent import ConsentPurpose
from app.schemas import PatientRegister, PatientResponse, BiometricVerify
from app.auth.dependencies import get_current_user, require_doctor, require_admin
from app.services.biometric import hash_fingerprint, hash_face, verify_fingerprint, verify_face
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
    Supports both fingerprint and face biometrics (both OPTIONAL).
    At least one biometric should be provided for identity verification.
    Only doctors and admins can register patients.
    """
    # Validate: at least one biometric provided
    if not patient_data.fingerprint_data and not patient_data.face_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one biometric (fingerprint or face) must be provided"
        )
    
    # Process fingerprint if provided
    if patient_data.fingerprint_data:
        fingerprint_hash = hash_fingerprint(patient_data.fingerprint_data)
        
        # Check if fingerprint already exists
        existing_fingerprint = db.query(BiometricHash).filter(
            BiometricHash.biometric_hash == fingerprint_hash,
            BiometricHash.biometric_type == BiometricType.FINGERPRINT.value
        ).first()
        
        if existing_fingerprint:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This fingerprint is already registered"
            )
    else:
        fingerprint_hash = None
    
    # Process face if provided
    if patient_data.face_data:
        face_hash = hash_face(patient_data.face_data)
        
        # Check if face already exists
        existing_face = db.query(BiometricHash).filter(
            BiometricHash.biometric_hash == face_hash,
            BiometricHash.biometric_type == BiometricType.FACE.value
        ).first()
        
        if existing_face:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This face is already registered"
            )
    else:
        face_hash = None
    
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
    
    # Store fingerprint biometric hash if provided
    if fingerprint_hash:
        fingerprint_bio = BiometricHash(
            patient_id=patient.id,
            biometric_type=BiometricType.FINGERPRINT.value,
            biometric_hash=fingerprint_hash,
            hash_algorithm="HMAC-SHA256",
            is_active=True
        )
        db.add(fingerprint_bio)
    
    # Store face biometric hash if provided
    if face_hash:
        face_bio = BiometricHash(
            patient_id=patient.id,
            biometric_type=BiometricType.FACE.value,
            biometric_hash=face_hash,
            hash_algorithm="HMAC-SHA256",
            is_active=True
        )
        db.add(face_bio)
    
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
    biometric_types = []
    if fingerprint_hash:
        biometric_types.append("fingerprint")
    if face_hash:
        biometric_types.append("face")
    
    AuditService.log(
        db=db,
        action=AuditAction.PATIENT_REGISTERED,
        actor=current_user,
        resource_type="patient",
        resource_id=patient.id,
        description=f"Patient registered: {patient.first_name} {patient.last_name} with biometrics: {', '.join(biometric_types)}",
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
    Verify fingerprint or face and return patient ID.
    Supports both fingerprint and face verification.
    At least one biometric must be provided.
    Used for patient lookup and identity verification.
    """
    patient_id = None
    verified_type = None
    
    # Try fingerprint verification if provided
    if verify_data.fingerprint_data:
        fingerprint_hash = hash_fingerprint(verify_data.fingerprint_data)
        
        biometric = db.query(BiometricHash).filter(
            BiometricHash.biometric_hash == fingerprint_hash,
            BiometricHash.biometric_type == BiometricType.FINGERPRINT.value,
            BiometricHash.is_active == True
        ).first()
        
        if biometric:
            patient_id = biometric.patient_id
            verified_type = "fingerprint"
    
    # Try face verification if provided and fingerprint didn't match
    if not patient_id and verify_data.face_data:
        face_hash = hash_face(verify_data.face_data)
        
        biometric = db.query(BiometricHash).filter(
            BiometricHash.biometric_hash == face_hash,
            BiometricHash.biometric_type == BiometricType.FACE.value,
            BiometricHash.is_active == True
        ).first()
        
        if biometric:
            patient_id = biometric.patient_id
            verified_type = "face"
    
    # No matching biometric found
    if not patient_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patient found with the provided biometric(s)"
        )
    
    # Get patient
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    
    if not patient or not patient.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or inactive"
        )
    
    return {
        "verified": True,
        "patient_id": patient.id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "verified_via": verified_type
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
    with_consent: bool = False,
    current_user: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    List all patients (doctors and admins only).
    If with_consent=True, only return patients for whom the current doctor has consent.
    """
    if with_consent and current_user.role.value == "doctor":
        # Get patients for whom this doctor has consent
        from app.models.consent import Consent, ConsentPurpose
        
        consents = db.query(Consent).filter(
            Consent.granted_to == current_user.id,
            Consent.granted == True,
            Consent.purpose == ConsentPurpose.TREATMENT
        ).all()
        
        patient_ids = [consent.patient_id for consent in consents]
        
        patients = db.query(Patient).filter(
            Patient.id.in_(patient_ids),
            Patient.is_active == True
        ).offset(skip).limit(limit).all()
    else:
        # Return all patients (for admins or when consent filtering is not requested)
        patients = db.query(Patient).filter(
            Patient.is_active == True
        ).offset(skip).limit(limit).all()
    
    return patients
