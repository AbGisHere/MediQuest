"""
Patient model for global patient identity.
Includes demographics and biometric linkage.
"""
from sqlalchemy import Column, String, DateTime, Date, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Patient(Base):
    """
    Patient model with global unique identifier.
    No dependency on Aadhaar or phone numbers.
    Country and hospital agnostic.
    """
    __tablename__ = "patients"
    
    # Global Patient UID (non-guessable, globally unique)
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    
    # Contact (optional)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Address (optional)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=False, default="India")
    postal_code = Column(String(20), nullable=True)
    
    # Emergency contact
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)
    
    # Registration info
    registered_by = Column(String(36), ForeignKey("users.id"), nullable=False)  # Doctor who registered
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Patient {self.id} - {self.first_name} {self.last_name}>"


class BiometricHash(Base):
    """
    Stores hashed biometric data (fingerprint).
    One fingerprint hash maps to one patient UID.
    No raw biometric data is stored.
    """
    __tablename__ = "biometric_hashes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, unique=True, index=True)
    fingerprint_hash = Column(String(64), nullable=False, unique=True, index=True)  # SHA-256 hash
    hash_algorithm = Column(String(20), default="SHA256", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    patient = relationship("Patient", backref="biometric")
    
    def __repr__(self):
        return f"<BiometricHash for patient {self.patient_id}>"
