"""
Vitals model for time-series medical data storage.
Optimized for TimescaleDB hypertables.
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Integer, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class VitalSource(str, enum.Enum):
    """Source of vital data."""
    DOCTOR = "doctor"
    DEVICE = "device"
    WEARABLE = "wearable"
    MANUAL = "manual"
    EXTERNAL = "external"


class VitalType(str, enum.Enum):
    """Types of vital measurements."""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE_SYSTOLIC = "bp_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "bp_diastolic"
    OXYGEN_SATURATION = "spo2"
    TEMPERATURE = "temperature"
    GLUCOSE = "glucose"
    WEIGHT = "weight"
    HEIGHT = "height"
    BMI = "bmi"
    RESPIRATORY_RATE = "respiratory_rate"
    ECG = "ecg"
    STEPS = "steps"
    SLEEP_HOURS = "sleep_hours"
    CALORIES = "calories"


class Vital(Base):
    """
    Time-series vital signs data.
    This table should be converted to a TimescaleDB hypertable.
    """
    __tablename__ = "vitals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Measurement
    vital_type = Column(String(50), nullable=False)  # Using string for flexibility with enum
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Source tracking
    source = Column(String(20), nullable=False)  # doctor/device/wearable/manual/external
    source_id = Column(String(36), nullable=True)  # ID of doctor/device that recorded
    
    # Timestamp (for time-series)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Data integrity
    checksum = Column(String(64), nullable=True)  # SHA-256 checksum for offline validation
    batch_id = Column(String(36), nullable=True)  # For batch uploads
    
    # Additional context
    notes = Column(Text, nullable=True)
    
    # Upload tracking
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", backref="vitals")
    
    def __repr__(self):
        return f"<Vital {self.vital_type}={self.value}{self.unit} for {self.patient_id}>"


# Create composite index for efficient time-series queries
Index('idx_vitals_patient_time', Vital.patient_id, Vital.recorded_at.desc())
Index('idx_vitals_type_time', Vital.vital_type, Vital.recorded_at.desc())
Index('idx_vitals_batch', Vital.batch_id)
