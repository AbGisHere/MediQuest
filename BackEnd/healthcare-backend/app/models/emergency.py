"""
Emergency access model for crash/emergency scenarios.
Time-limited bypass with full audit trail.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class EmergencyAccess(Base):
    """
    Emergency access records for crash scenarios.
    Bypasses consent with full audit logging.
    Auto-expires after configured duration.
    """
    __tablename__ = "emergency_access"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Access details
    triggered_by = Column(String(36), ForeignKey("users.id"), nullable=False)  # Who triggered emergency
    trigger_reason = Column(Text, nullable=False)  # Reason for emergency access
    trigger_keyword = Column(String(50), nullable=True)  # "crash", "emergency", etc.
    
    # Access window
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Auto-calculated based on config
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    terminated = Column(Boolean, default=False, nullable=False)
    terminated_at = Column(DateTime(timezone=True), nullable=True)
    terminated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    termination_reason = Column(Text, nullable=True)
    
    # Notification
    hospital_notified = Column(Boolean, default=False, nullable=False)
    notification_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Access tracking
    access_count = Column(Integer, default=0, nullable=False)  # Number of times data was accessed
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("Patient", backref="emergency_accesses")
    
    def __repr__(self):
        return f"<EmergencyAccess for {self.patient_id} - expires {self.expires_at}>"
    
    @property
    def has_expired(self) -> bool:
        """Check if emergency access has expired."""
        from datetime import datetime, timezone
        if self.terminated:
            return True
        return datetime.now(timezone.utc) > self.expires_at
