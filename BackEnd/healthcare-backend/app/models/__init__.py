"""
Models package initialization.
Imports all models for easy access.
"""
from app.models.user import User, UserRole
from app.models.patient import Patient, BiometricHash
from app.models.consent import Consent, ConsentPurpose
from app.models.vitals import Vital, VitalSource, VitalType
from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.device import Device, DeviceType
from app.models.emergency import EmergencyAccess
from app.models.audit import AuditLog, AuditAction, HealthCondition, Allergy

__all__ = [
    # User
    "User",
    "UserRole",
    # Patient
    "Patient",
    "BiometricHash",
    # Consent
    "Consent",
    "ConsentPurpose",
    # Vitals
    "Vital",
    "VitalSource",
    "VitalType",
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
