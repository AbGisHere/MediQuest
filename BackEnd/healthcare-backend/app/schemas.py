"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime, date
from app.models.user import UserRole
from app.models.consent import ConsentPurpose
from app.models.vitals import VitalSource, VitalType
from app.models.alert import AlertSeverity, AlertType
from app.models.device import DeviceType


# ============== Authentication Schemas ==============

class UserRegister(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole


class UserLogin(BaseModel):
    """User login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# ============== Patient Schemas ==============

class PatientRegister(BaseModel):
    """Patient registration request."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    postal_code: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    fingerprint_data: str  # Raw fingerprint data (will be hashed)


class PatientResponse(BaseModel):
    """Patient response."""
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str]
    blood_group: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    country: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class BiometricVerify(BaseModel):
    """Biometric verification request."""
    fingerprint_data: str


# ============== Consent Schemas ==============

class ConsentGrant(BaseModel):
    """Grant consent request."""
    patient_id: str
    purpose: ConsentPurpose
    granted_to_id: Optional[str] = None
    consent_text: Optional[str] = None
    expiry_date: Optional[datetime] = None


class ConsentRevoke(BaseModel):
    """Revoke consent request."""
    patient_id: str
    purpose: ConsentPurpose
    granted_to_id: Optional[str] = None


class ConsentResponse(BaseModel):
    """Consent response."""
    id: str
    patient_id: str
    purpose: ConsentPurpose
    granted: bool
    granted_at: Optional[datetime]
    revoked_at: Optional[datetime]
    expiry_date: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Vitals Schemas ==============

class VitalCreate(BaseModel):
    """Create vital request."""
    patient_id: str
    vital_type: str
    value: float
    unit: str
    source: str = "doctor"
    source_id: Optional[str] = None
    recorded_at: datetime
    notes: Optional[str] = None
    checksum: Optional[str] = None


class VitalBatchCreate(BaseModel):
    """Batch create vitals request."""
    vitals: List[VitalCreate]
    batch_id: Optional[str] = None


class VitalResponse(BaseModel):
    """Vital response."""
    id: str
    patient_id: str
    vital_type: str
    value: float
    unit: str
    source: str
    recorded_at: datetime
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============== Alert Schemas ==============

class AlertResponse(BaseModel):
    """Alert response."""
    id: str
    patient_id: str
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    trigger_value: Optional[float]
    acknowledged: bool
    resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    """Acknowledge alert request."""
    alert_id: str


class AlertResolve(BaseModel):
    """Resolve alert request."""
    alert_id: str
    resolution_notes: Optional[str] = None


# ============== Health Profile Schemas ==============

class HealthConditionCreate(BaseModel):
    """Create health condition."""
    patient_id: str
    condition_name: str
    diagnosed_date: Optional[datetime] = None
    severity: Optional[str] = None
    notes: Optional[str] = None


class AllergyCreate(BaseModel):
    """Create allergy."""
    patient_id: str
    allergen: str
    reaction: Optional[str] = None
    severity: Optional[str] = None
    diagnosed_date: Optional[datetime] = None


class HealthProfileResponse(BaseModel):
    """Unified health profile response."""
    patient: PatientResponse
    chronic_conditions: List[dict]
    allergies: List[dict]
    recent_vitals: List[VitalResponse]
    recent_alerts: List[AlertResponse]
    last_updated: datetime


# ============== Device Schemas ==============

class DeviceRegister(BaseModel):
    """Device registration request."""
    device_name: str
    device_type: str
    manufacturer: Optional[str] = None
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    patient_id: Optional[str] = None
    firmware_version: Optional[str] = None
    software_version: Optional[str] = None


class DeviceResponse(BaseModel):
    """Device response."""
    id: str
    device_name: str
    device_type: str
    serial_number: Optional[str]
    is_active: bool
    last_heartbeat: Optional[datetime]
    registered_at: datetime
    
    class Config:
        from_attributes = True


class DeviceIngest(BaseModel):
    """Device data ingestion request."""
    device_id: str
    api_key: str
    vitals: List[VitalCreate]


# ============== Emergency Schemas ==============

class EmergencyTrigger(BaseModel):
    """Emergency access trigger request."""
    patient_id: str
    trigger_reason: str
    trigger_keyword: Optional[str] = "emergency"


class EmergencyAccessResponse(BaseModel):
    """Emergency access response."""
    id: str
    patient_id: str
    granted_at: datetime
    expires_at: datetime
    is_active: bool
    hospital_notified: bool
    
    class Config:
        from_attributes = True


# ============== Audit Schemas ==============

class AuditLogResponse(BaseModel):
    """Audit log response."""
    id: str
    action: str
    actor_id: Optional[str]
    actor_role: Optional[str]
    resource_type: Optional[str]
    resource_id: Optional[str]
    description: Optional[str]
    success: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
