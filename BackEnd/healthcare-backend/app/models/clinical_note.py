"""
Clinical Notes Model
Stores encrypted clinical notes with role-based access control.
"""
import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NoteCategory(str, enum.Enum):
    """Categories for clinical notes."""
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    OBSERVATION = "observation"
    PRESCRIPTION = "prescription"
    LAB_RESULTS = "lab_results"
    PROCEDURE = "procedure"
    FOLLOW_UP = "follow_up"
    GENERAL = "general"


class EncryptionRole(str, enum.Enum):
    """Indicates which encryption key was used."""
    DOCTOR = "doctor"
    ADMIN = "admin"
    PATIENT = "patient"


class ClinicalNote(Base):
    """
    Model for storing clinical notes with encryption.
    
    Access Control:
    - Doctor: Can add notes (encrypted with DOCTOR_KEY)
    - Patient: Can view only (decrypt with PATIENT_KEY)
    - Admin: Full edit (decrypt/encrypt with ADMIN_KEY)
    """
    __tablename__ = "clinical_notes"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    author_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Note Content (ENCRYPTED)
    note_content = Column(Text, nullable=False)  # Encrypted text
    encryption_role = Column(SQLEnum(EncryptionRole), nullable=False, default=EncryptionRole.DOCTOR)
    
    # Metadata
    category = Column(SQLEnum(NoteCategory), nullable=False, default=NoteCategory.GENERAL)
    is_sensitive = Column(Boolean, default=False)  # Extra sensitive notes
    is_active = Column(Boolean, default=True)  # Soft delete support
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("Patient", backref="clinical_notes")
    author = relationship("User", backref="authored_notes")
    
    def __repr__(self):
        return f"<ClinicalNote {self.id} by {self.author_id} for {self.patient_id}>"
