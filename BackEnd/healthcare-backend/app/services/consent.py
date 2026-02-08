"""
Consent management service.
Handles consent checking and enforcement for DPDP compliance.
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.consent import Consent, ConsentPurpose
from app.models.user import User


class ConsentService:
    """Service for consent management and enforcement."""
    
    @staticmethod
    def check_consent(
        db: Session,
        patient_id: str,
        purpose: ConsentPurpose,
        doctor_id: Optional[str] = None
    ) -> bool:
        """
        Check if consent exists for a specific purpose.
        
        Args:
            db: Database session
            patient_id: Patient ID
            purpose: Purpose of data access
            doctor_id: Optional doctor ID for specific consent
            
        Returns:
            True if consent is granted and active, False otherwise
        """
        query = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.purpose == purpose,
            Consent.granted == True
        )
        
        # Check for specific doctor consent if provided
        if doctor_id:
            query = query.filter(
                (Consent.granted_to == doctor_id) | (Consent.granted_to == None)
            )
        
        consent = query.first()
        
        if not consent:
            return False
        
        # Check if consent is still active
        if consent.revoked_at:
            return False
        
        # Check expiry
        if consent.expiry_date and consent.expiry_date < datetime.now(timezone.utc):
            return False
        
        return True
    
    @staticmethod
    def grant_consent(
        db: Session,
        patient_id: str,
        purpose: ConsentPurpose,
        granted_by_id: str,
        granted_to_id: Optional[str] = None,
        consent_text: Optional[str] = None,
        expiry_date: Optional[datetime] = None
    ) -> Consent:
        """
        Grant consent for a patient.
        
        Args:
            db: Database session
            patient_id: Patient ID
            purpose: Purpose of consent
            granted_by_id: User ID granting consent
            granted_to_id: Optional doctor/entity receiving consent
            consent_text: Optional consent text
            expiry_date: Optional expiry date
            
        Returns:
            Created Consent instance
        """
        # Check if consent already exists
        existing = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.purpose == purpose,
            Consent.granted_to == granted_to_id
        ).first()
        
        if existing and existing.granted:
            # Already granted
            return existing
        
        consent = Consent(
            patient_id=patient_id,
            purpose=purpose,
            granted=True,
            granted_at=datetime.now(timezone.utc),
            granted_by=granted_by_id,
            granted_to=granted_to_id,
            consent_text=consent_text,
            expiry_date=expiry_date
        )
        
        db.add(consent)
        db.commit()
        db.refresh(consent)
        
        return consent
    
    @staticmethod
    def revoke_consent(
        db: Session,
        patient_id: str,
        purpose: ConsentPurpose,
        revoked_by_id: str,
        granted_to_id: Optional[str] = None
    ) -> Optional[Consent]:
        """
        Revoke consent.
        
        Args:
            db: Database session
            patient_id: Patient ID
            purpose: Purpose of consent
            revoked_by_id: User ID revoking consent
            granted_to_id: Optional specific doctor consent to revoke
            
        Returns:
            Updated Consent instance or None if not found
        """
        query = db.query(Consent).filter(
            Consent.patient_id == patient_id,
            Consent.purpose == purpose,
            Consent.granted == True
        )
        
        if granted_to_id:
            query = query.filter(Consent.granted_to == granted_to_id)
        
        consent = query.first()
        
        if not consent:
            return None
        
        consent.granted = False
        consent.revoked_at = datetime.now(timezone.utc)
        consent.revoked_by = revoked_by_id
        
        db.commit()
        db.refresh(consent)
        
        return consent
