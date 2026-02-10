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
from app.models.clinical_note import NoteCategory, EncryptionRole
from app.models.blood_report import ReportType


# Note: Include all existing schemas first (not showing them here to save space)
# ... (keep all existing schemas as they are)

# ============== Clinical Notes Schemas ==============

class ClinicalNoteCreate(BaseModel):
    """Create a new clinical note."""
    patient_id: str
    content: str = Field(..., min_length=1, max_length=10000)
    category: NoteCategory = NoteCategory.GENERAL
    is_sensitive: bool = False


class ClinicalNoteUpdate(BaseModel):
    """Update an existing note (admin only)."""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    category: Optional[NoteCategory] = None
    is_sensitive: Optional[bool] = None


class ClinicalNoteResponse(BaseModel):
    """Clinical note response."""
    id: str
    patient_id: str
    author_id: str
    author_name: Optional[str] = None  # Will be populated from user
    content: str  # Decrypted content (only if user has permission)
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
    
    # CBC Values
    hemoglobin: Optional[float] = None
    wbc_count: Optional[float] = None
    rbc_count: Optional[float] = None
    platelet_count: Optional[float] = None
    hematocrit: Optional[float] = None
    mcv: Optional[float] = None
    mch: Optional[float] = None
    mchc: Optional[float] = None
    
    # Glucose
    glucose_fasting: Optional[float] = None
    glucose_random: Optional[float] = None
    glucose_pp: Optional[float] = None
    hba1c: Optional[float] = None
    
    # Lipid Panel
    cholesterol_total: Optional[float] = None
    cholesterol_hdl: Optional[float] = None
    cholesterol_ldl: Optional[float] = None
    cholesterol_vldl: Optional[float] = None
    triglycerides: Optional[float] = None
    
    # Liver Function
    sgot: Optional[float] = None
    sgpt: Optional[float] = None
    alkaline_phosphatase: Optional[float] = None
    bilirubin_total: Optional[float] = None
    bilirubin_direct: Optional[float] = None
    bilirubin_indirect: Optional[float] = None
    total_protein: Optional[float] = None
    albumin: Optional[float] = None
    globulin: Optional[float] = None
    
    # Kidney Function
    creatinine: Optional[float] = None
    urea: Optional[float] = None
    uric_acid: Optional[float] = None
    bun: Optional[float] = None
    egfr: Optional[float] = None
    
    # Thyroid
    tsh: Optional[float] = None
    t3: Optional[float] = None
    t4: Optional[float] = None
    
    # Electrolytes
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    chloride: Optional[float] = None
    
    # Others
    calcium: Optional[float] = None
    phosphorus: Optional[float] = None
    magnesium: Optional[float] = None
    iron: Optional[float] = None
    vitamin_d: Optional[float] = None
    vitamin_b12: Optional[float] = None
    
    # Metadata
    other_values: Optional[dict] = None
    parsing_confidence: Optional[float] = None
    parsing_notes: Optional[str] = None
    pdf_file_size: Optional[float] = None
    
    uploaded_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BloodReportSummary(BaseModel):
    """Summary view of a blood report (without all values)."""
    id: str
    patient_id: str
    report_type: str
    test_date: Optional[date] = None
    lab_name: Optional[str] = None
    parsing_confidence: Optional[float] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
