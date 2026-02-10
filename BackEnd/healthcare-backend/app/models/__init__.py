"""
Models package initialization.
Imports all models for easy access.
"""
from app.models.user import User, UserRole
from app.models.patient import Patient, BiometricHash, BiometricType
from app.models.consent import Consent, ConsentPurpose
from app.models.vitals import Vital, VitalSource, VitalType
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.device import Device, DeviceType
from app.models.emergency import EmergencyAccess
from app.models.audit import AuditLog, AuditAction, HealthCondition, Allergy
from app.models.medical_test import MedicalTest, TestType, TestResult, TestSource
from app.models.clinical_note import ClinicalNote, NoteCategory, EncryptionRole
from app.models.blood_report import BloodReport, ReportType

__all__ = [
    # User
    "User",
    "UserRole",
    # Patient
    "Patient",
    "BiometricHash",
    "BiometricType",
    # Consent
    "Consent",
    "ConsentPurpose",
    # Vitals
    "Vital",
    "VitalSource",
    "VitalType",
    # Medical Tests
    "MedicalTest",
    "TestType",
    "TestResult",
    "TestSource",
    # Clinical Notes
    "ClinicalNote",
    "NoteCategory",
    "EncryptionRole",
    # Blood Reports
    "BloodReport",
    "ReportType",
    # Alert
    "Alert",
    "AlertSeverity",
    "AlertType",
    # Device
    "Device",
    "DeviceType",
    # Emergency
    "EmergencyAccess",
    # Audit
    "AuditLog",
    "AuditAction",
    "HealthCondition",
    "Allergy",
]

