"""
Medical Tests model for point-in-time diagnostic results (RDTs & screenings).
This is separate from continuous vitals and represents discrete test results.
"""
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text, Enum as SQLEnum, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
import enum


class TestType(str, enum.Enum):
    """Types of medical diagnostic tests."""
    MALARIA_RDT = "malaria_rdt"
    DENGUE_NS1 = "dengue_ns1"
    HIV_1_2 = "hiv_1_2"
    HEPATITIS_B_RDT = "hepatitis_b_rdt"
    HEPATITIS_C_RDT = "hepatitis_c_rdt"
    SYPHILIS_RPR = "syphilis_rpr"
    CRP_LATEX = "crp_latex"
    SICKLE_CELL_TEST = "sickle_cell_test"
    TB_LAM = "tb_lam"
    PREGNANCY_HCG = "pregnancy_hcg"


class TestResult(str, enum.Enum):
    """Standard test result values."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    INCONCLUSIVE = "inconclusive"
    NUMERIC = "numeric"  # For numeric results (e.g., CRP levels)


class TestSource(str, enum.Enum):
    """Source of test data."""
    DOCTOR = "doctor"
    DEVICE = "device"
    MANUAL = "manual"
    LAB = "lab"


class MedicalTest(Base):
    """
    Point-in-time diagnostic test results.
    Supports RDTs, screenings, and other discrete medical tests.
    """
    __tablename__ = "medical_tests"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Test information
    test_type = Column(String(50), nullable=False)  # Using string for flexibility
    result = Column(String(50), nullable=False)  # positive/negative/inconclusive or numeric
    numeric_value = Column(Float, nullable=True)  # For numeric results (e.g., CRP: 12.5 mg/L)
    unit = Column(String(20), nullable=True)  # Unit if numeric
    
    # Source tracking
    source = Column(String(20), nullable=False)  # doctor/device/manual/lab
    source_id = Column(String(36), nullable=True)  # ID of doctor/device/lab
    
    # Timestamp
    performed_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Additional context
    notes = Column(Text, nullable=True)
    batch_id = Column(String(36), nullable=True)  # For batch test uploads
    
    # Upload tracking
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    patient = relationship("Patient", backref="medical_tests")
    
    def __repr__(self):
        return f"<MedicalTest {self.test_type}={self.result} for {self.patient_id}>"


# Create indices for efficient queries
Index('idx_medical_tests_patient_time', MedicalTest.patient_id, MedicalTest.performed_at.desc())
Index('idx_medical_tests_type', MedicalTest.test_type)
Index('idx_medical_tests_batch', MedicalTest.batch_id)
