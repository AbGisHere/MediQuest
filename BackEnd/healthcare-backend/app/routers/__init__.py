# Routers package
# Export all routers for easy import in main.py

from app.routers import auth, patients, vitals, consent, emergency, health_profile, device_ingest, notes, blood_reports, emergency_trigger

__all__ = [
    "auth",
    "patients",
    "vitals",
    "consent",
    "emergency",
    "health_profile",
    "device_ingest",
    "notes",
    "blood_reports",
    "emergency_trigger",
]
