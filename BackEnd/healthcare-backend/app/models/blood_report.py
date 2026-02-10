"""
Blood Report Model
Stores parsed blood test reports from PDF uploads.
"""
import enum
import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Text, Float, Date, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ReportType(str, enum.Enum):
    """Types of blood reports."""
    CBC = "cbc"  # Complete Blood Count
    LIPID_PANEL = "lipid_panel"
    LIVER_FUNCTION = "liver_function"
    KIDNEY_FUNCTION = "kidney_function"
    THYROID = "thyroid"
    DIABETES = "diabetes"
    GENERAL = "general"
    OTHER = "other"


class BloodReport(Base):
    """
    Model for storing blood test reports extracted from PDFs.
    Only admins can upload PDFs.
    """
    __tablename__ = "blood_reports"
    
    # Primary Key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Relationships
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Report Metadata
    report_type = Column(SQLEnum(ReportType), nullable=False, default=ReportType.GENERAL)
    test_date = Column(Date, nullable=True)  # Date when test was performed
    lab_name = Column(String(200), nullable=True)
    
    # PDF Storage
    pdf_file_path = Column(String(500), nullable=False)  # Path to stored PDF
    pdf_file_hash = Column(String(64), nullable=False)  # SHA-256 hash for integrity
    pdf_file_size = Column(Float, nullable=True)  # Size in MB
    extracted_text = Column(Text, nullable=True)  # Full extracted text from PDF
    
    # CBC Values (Complete Blood Count)
    hemoglobin = Column(Float, nullable=True)  # g/dL
    wbc_count = Column(Float, nullable=True)  # cells/μL
    rbc_count = Column(Float, nullable=True)  # million cells/μL
    platelet_count = Column(Float, nullable=True)  # cells/μL
    hematocrit = Column(Float, nullable=True)  # %
    mcv = Column(Float, nullable=True)  # Mean Corpuscular Volume
    mch = Column(Float, nullable=True)  # Mean Corpuscular Hemoglobin
    mchc = Column(Float, nullable=True)  # Mean Corpuscular Hemoglobin Concentration
    
    # Glucose Values
    glucose_fasting = Column(Float, nullable=True)  # mg/dL
    glucose_random = Column(Float, nullable=True)  # mg/dL
    glucose_pp = Column(Float, nullable=True)  # Post-Prandial
    hba1c = Column(Float, nullable=True)  # %
    
    # Lipid Panel
    cholesterol_total = Column(Float, nullable=True)  # mg/dL
    cholesterol_hdl = Column(Float, nullable=True)  # mg/dL (Good cholesterol)
    cholesterol_ldl = Column(Float, nullable=True)  # mg/dL (Bad cholesterol)
    cholesterol_vldl = Column(Float, nullable=True)  # mg/dL
    triglycerides = Column(Float, nullable=True)  # mg/dL
    
    # Liver Function Tests
    sgot = Column(Float, nullable=True)  # AST - U/L
    sgpt = Column(Float, nullable=True)  # ALT - U/L
    alkaline_phosphatase = Column(Float, nullable=True)  # U/L
    bilirubin_total = Column(Float, nullable=True)  # mg/dL
    bilirubin_direct = Column(Float, nullable=True)  # mg/dL
    bilirubin_indirect = Column(Float, nullable=True)  # mg/dL
    total_protein = Column(Float, nullable=True)  # g/dL
    albumin = Column(Float, nullable=True)  # g/dL
    globulin = Column(Float, nullable=True)  # g/dL
    
    # Kidney Function Tests
    creatinine = Column(Float, nullable=True)  # mg/dL
    urea = Column(Float, nullable=True)  # mg/dL
    uric_acid = Column(Float, nullable=True)  # mg/dL
    bun = Column(Float, nullable=True)  # Blood Urea Nitrogen - mg/dL
    egfr = Column(Float, nullable=True)  # Estimated Glomerular Filtration Rate
    
    # Thyroid Function
    tsh = Column(Float, nullable=True)  # μIU/mL
    t3 = Column(Float, nullable=True)  # ng/dL
    t4 = Column(Float, nullable=True)  # μg/dL
    
    # Electrolytes
    sodium = Column(Float, nullable=True)  # mEq/L
    potassium = Column(Float, nullable=True)  # mEq/L
    chloride = Column(Float, nullable=True)  # mEq/L
    
    # Other Common Values
    calcium = Column(Float, nullable=True)  # mg/dL
    phosphorus = Column(Float, nullable=True)  # mg/dL
    magnesium = Column(Float, nullable=True)  # mg/dL
    iron = Column(Float, nullable=True)  # μg/dL
    vitamin_d = Column(Float, nullable=True)  # ng/mL
    vitamin_b12 = Column(Float, nullable=True)  # pg/mL
    
    # Flexible storage for any other values not covered above
    other_values = Column(JSON, nullable=True)
    
    # Parsing Metadata
    parsing_confidence = Column(Float, nullable=True)  # 0-100% confidence
    parsing_notes = Column(Text, nullable=True)  # Notes about parsing issues
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("Patient", backref="blood_reports")
    uploader = relationship("User", backref="uploaded_reports")
    
    def __repr__(self):
        return f"<BloodReport {self.id} for {self.patient_id} ({self.report_type})>"
