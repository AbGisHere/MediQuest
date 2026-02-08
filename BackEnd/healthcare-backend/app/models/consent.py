"""
Consent model for DPDP compliance.
Implements purpose-based consent with grant/revoke capabilities.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class ConsentPurpose(str, enum.Enum):
    """Purpose enumeration for consent."""
    TREATMENT = "treatment"
    EMERGENCY = "emergency"
    RESEARCH = "research"
    ANALYTICS = "analytics"
    THIRD_PARTY = "third_party"


class Consent(Base):
    """
    Consent model for explicit patient consent tracking.
    Required for all medical data access except emergency.
    """
    __tablename__ = "consents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    purpose = Column(Enum(ConsentPurpose), nullable=False)
    granted = Column(Boolean, default=True, nullable=False)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    granted_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # User who granted (may be patient themselves)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revoked_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Additional consent details
    granted_to = Column(String(36), ForeignKey("users.id"), nullable=True)  # Doctor/entity receiving consent
    consent_text = Column(Text, nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("Patient", backref="consents")
    
    def __repr__(self):
        status = "granted" if self.granted else "revoked"
        return f"<Consent {self.id} - {self.purpose} ({status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        if not self.granted:
            return False
        if self.revoked_at:
            return False
        if self.expiry_date and self.expiry_date < func.now():
            return False
        return True
