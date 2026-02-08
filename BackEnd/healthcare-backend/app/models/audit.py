"""
Audit log model for immutable compliance tracking.
Logs all critical actions for DPDP compliance.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum, Boolean
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    
    # Patient
    PATIENT_REGISTERED = "patient_registered"
    PATIENT_UPDATED = "patient_updated"
    PATIENT_DELETED = "patient_deleted"
    PATIENT_VIEWED = "patient_viewed"
    
    # Consent
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    CONSENT_CHECKED = "consent_checked"
    
    # Medical Data
    VITAL_UPLOADED = "vital_uploaded"
    VITAL_VIEWED = "vital_viewed"
    VITAL_DELETED = "vital_deleted"
    BATCH_UPLOAD = "batch_upload"
    
    # Emergency
    EMERGENCY_TRIGGERED = "emergency_triggered"
    EMERGENCY_ACCESS = "emergency_access"
    EMERGENCY_TERMINATED = "emergency_terminated"
    
    # Device
    DEVICE_REGISTERED = "device_registered"
    DEVICE_INGESTION = "device_ingestion"
    
    # Admin
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    USER_UPDATED = "user_updated"
    
    # Security
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    BRUTE_FORCE_DETECTED = "brute_force_detected"
    UNAUTHORIZED_ACCESS = "unauthorized_access"


class AuditLog(Base):
    """
    Immutable audit log for compliance.
    Records all critical system actions.
    Never updated or deleted (except by retention policy).
    """
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Who performed the action
    actor_role = Column(String(20), nullable=True)  # Role at time of action
    
    # Resource
    resource_type = Column(String(50), nullable=True)  # patient, vital, device, etc.
    resource_id = Column(String(36), nullable=True, index=True)  # ID of resource affected
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Context
    description = Column(Text, nullable=True)
    audit_metadata = Column(JSON, nullable=True)  # Additional context
    
    # Result
    success = Column(Boolean, nullable=False, default=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamp (immutable)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.actor_id} at {self.created_at}>"


# Additional audit table for health conditions and allergies

class HealthCondition(Base):
    """Patient chronic health conditions."""
    __tablename__ = "health_conditions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    condition_name = Column(String(200), nullable=False)
    diagnosed_date = Column(DateTime(timezone=True), nullable=True)
    diagnosed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Allergy(Base):
    """Patient allergies."""
    __tablename__ = "allergies"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    allergen = Column(String(200), nullable=False)
    reaction = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # mild, moderate, severe
    diagnosed_date = Column(DateTime(timezone=True), nullable=True)
    diagnosed_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
