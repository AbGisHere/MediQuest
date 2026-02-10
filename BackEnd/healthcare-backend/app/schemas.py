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
from app.models.medical_test import TestType, TestResult, TestSource


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
    fingerprint_data: Optional[str] = None  # Raw fingerprint data (will be hashed) - OPTIONAL
    face_data: Optional[str] = None  # Raw face data (will be hashed) - OPTIONAL


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
    """Biometric verification request - supports both fingerprint and face."""
    fingerprint_data: Optional[str] = None  # At least one must be provided
    face_data: Optional[str] = None  # At least one must be provided
    
    @validator('face_data')
    def check_at_least_one_biometric(cls, v, values):
        """Ensure at least one biometric is provided."""
        if not v and not values.get('fingerprint_data'):
            raise ValueError('At least one biometric (fingerprint or face) must be provided')
        return v


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
    """Device data ingestion request - FAULT TOLERANT."""
    device_id: str
    api_key: str
    vitals: Optional[List[VitalCreate]] = []  # OPTIONAL - missing vitals OK
    medical_tests: Optional[List['MedicalTestCreate']] = []  # OPTIONAL - missing tests OK


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


# ============== Medical Test Schemas ==============

class MedicalTestCreate(BaseModel):
    """Create medical test request."""
    patient_id: str
    test_type: str  # malaria_rdt, dengue_ns1, hiv_1_2, etc.
    result: str  # positive/negative/inconclusive/numeric
    numeric_value: Optional[float] = None  # For numeric results (e.g., CRP levels)
    unit: Optional[str] = None  # Unit if numeric
    source: str = "device"  # doctor/device/manual/lab
    source_id: Optional[str] = None
    performed_at: datetime
    notes: Optional[str] = None


class MedicalTestBatchCreate(BaseModel):
    """Batch create medical tests request."""
    tests: List[MedicalTestCreate]
    batch_id: Optional[str] = None


class MedicalTestResponse(BaseModel):
    """Medical test response."""
    id: str
    patient_id: str
    test_type: str
    result: str
    numeric_value: Optional[float]
    unit: Optional[str]
    source: str
    performed_at: datetime
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============== Expanded Device Ingestion (Fault-Tolerant) ==============

class FaultTolerantDeviceIngest(BaseModel):
    """
    Fault-tolerant device ingestion - accepts partial payloads.
    CRITICAL: Backend must NOT crash if any metric is missing.
    All vitals and tests are OPTIONAL.
    """
    device_id: str
    api_key: str
    patient_id: str  # Required for consent checking
    
    # All vitals are OPTIONAL - missing data is OK
    heart_rate: Optional[float] = None
    bp_systolic: Optional[float] = None
    bp_diastolic: Optional[float] = None
    spo2: Optional[float] = None
    temperature: Optional[float] = None
    glucose: Optional[float] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    bmi: Optional[float] = None
    respiratory_rate: Optional[float] = None
    ecg: Optional[str] = None  # ECG data as string/JSON
    steps: Optional[int] = None
    sleep_hours: Optional[float] = None
    calories: Optional[float] = None
    
    # Medical tests are OPTIONAL
    medical_tests: Optional[List[MedicalTestCreate]] = []
    
    # Metadata
    recorded_at: Optional[datetime] = None  # OPTIONAL - will use current time if missing
    batch_id: Optional[str] = None


# ============== Clinical Notes Schemas ==============

class ClinicalNoteCreate(BaseModel):
    """Create a new clinical note."""
    patient_id: str
    content: str = Field(..., min_length=1, max_length=10000)
    category: str = "general"  # Will be validated as NoteCategory
    is_sensitive: bool = False


class ClinicalNoteUpdate(BaseModel):
    """Update an existing note (admin only)."""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[str] = None
    is_sensitive: Optional[bool] = None


class ClinicalNoteResponse(BaseModel):
    """Clinical note response."""
    id: str
    patient_id: str
    author_id: str
    author_name: Optional[str] = None
    content: str  # Decrypted content
    category: str
    is_sensitive: bool
    encryption_role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Blood Report Schemas ==============

class BloodReportResponse(BaseModel):
    """Blood report response."""
    id: str
    patient_id: str
    uploaded_by: str
    uploader_name: Optional[str] = None
    report_type: str
    test_date: Optional[date] = None
    lab_name: Optional[str] = None
    hemoglobin: Optional[float] = None
    wbc_count: Optional[float] = None
    rbc_count: Optional[float] = None
    platelet_count: Optional[float] = None
    glucose_fasting: Optional[float] = None
    glucose_random: Optional[float] = None
    cholesterol_total: Optional[float] = None
    cholesterol_hdl: Optional[float] = None
    cholesterol_ldl: Optional[float] = None
    triglycerides: Optional[float] = None
    sgot: Optional[float] = None
    sgpt: Optional[float] = None
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    parsing_confidence: Optional[float] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class BloodReportSummary(BaseModel):
    """Summary view of a blood report."""
    id: str
    patient_id: str
    report_type: str
    test_date: Optional[date] = None
    parsing_confidence: Optional[float] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


# ============== Emergency Trigger Detection Schemas ==============

class EmergencyTriggerInput(BaseModel):
    """Input for emergency trigger detection."""
    input_text: str  # Voice-to-text or text input
    patient_identifier: Optional[str] = None  # Optional patient ID/phone/name
    location: Optional[str] = None  # GPS coordinates or location description
    
    class Config:
        json_schema_extra = {
            "example": {
                "input_text": "Emergency! Patient collapsed. Need immediate help.",
                "patient_identifier": "patient-uuid-or-phone",
                "location": "City Hospital, Building A"
            }
        }


class TriggerDetectionResult(BaseModel):
    """Result of trigger detection."""
    triggered: bool
    confidence: float
    detected_words: List[str]
    input_text: str
    timestamp: str


class EmergencyMedicalInfo(BaseModel):
    """Emergency medical information (read-only)."""
    patient_id: str
    name: str
    age: Optional[int] = None
    blood_group: str
    emergency_contact: str
    phone: str
    allergies: List[dict] = []
    conditions: List[dict] = []
    medications: List[dict] = []
    latest_vitals: dict = {}
    access_type: str  # Always "EMERGENCY_READ_ONLY"
    access_granted_at: str
    note: str  # Warning about read-only access


class EmergencyTriggerResponse(BaseModel):
    """Complete response for emergency trigger."""
    detected: bool
    detection_details: TriggerDetectionResult
    medical_info: Optional[EmergencyMedicalInfo] = None
    message: str
