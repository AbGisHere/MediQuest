"""
Device model for hardware and wearable integration.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class DeviceType(str, enum.Enum):
    """Types of medical devices."""
    GLUCOSE_MONITOR = "glucose_monitor"
    BLOOD_PRESSURE_MONITOR = "bp_monitor"
    PULSE_OXIMETER = "pulse_oximeter"
    ECG_MONITOR = "ecg_monitor"
    THERMOMETER = "thermometer"
    SMARTWATCH = "smartwatch"
    FITNESS_TRACKER = "fitness_tracker"
    CONTINUOUS_GLUCOSE_MONITOR = "cgm"
    HEART_RATE_MONITOR = "hr_monitor"
    WEIGHING_SCALE = "weighing_scale"


class Device(Base):
    """
    Registered medical devices and wearables.
    Each device has authentication and health monitoring.
    """
    __tablename__ = "devices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Device info
    device_name = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=False)
    manufacturer = Column(String(200), nullable=True)
    model_number = Column(String(100), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True, index=True)
    
    # Authentication
    api_key_hash = Column(String(255), nullable=False)  # Hashed API key for device auth
    
    # Association
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=True)  # Device may be assigned to patient
    registered_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Firmware/Version
    firmware_version = Column(String(50), nullable=True)
    software_version = Column(String(50), nullable=True)
    
    # Health monitoring
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Device-specific data
    device_metadata = Column(JSON, nullable=True)  # Additional device-specific data
    
    # Timestamps
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    patient = relationship("Patient", backref="devices")
    
    def __repr__(self):
        return f"<Device {self.device_name} ({self.device_type})>"
