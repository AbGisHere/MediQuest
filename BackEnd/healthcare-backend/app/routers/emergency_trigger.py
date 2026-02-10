"""
Emergency Trigger Detection Router
Handles emergency trigger word detection and provides read-only medical information.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models import Patient, BiometricHash, HealthCondition, Allergy, Vital, EmergencyAccess, AuditLog
from app.schemas import (
    EmergencyTriggerInput,
    EmergencyTriggerResponse,
    TriggerDetectionResult,
    EmergencyMedicalInfo
)
from app.services.trigger_detection import TriggerWordDetector

router = APIRouter(prefix="/emergency-trigger", tags=["Emergency Trigger"])


@router.post("/detect", response_model=EmergencyTriggerResponse)
async def detect_emergency_trigger(
    trigger_input: EmergencyTriggerInput,
    db: Session = Depends(get_db)
):
    """
    Detect emergency trigger words and provide read-only medical information.
    
    **Trigger Words:** emergency, help, urgent, critical, medical emergency, etc.
    
    **Flow:**
    1. Analyze input text for trigger words
    2. If triggered, extract patient identifier
    3. Return critical medical info (READ-ONLY)
    
    **Use Cases:**
    - Voice-activated emergency ("Help! Emergency!")
    - Quick emergency access for first responders
    - Automated emergency response systems
    
    **Security:**
    - Read-only access
    - Logged in audit trail
    - No authentication required (emergency use)
    - Limited to critical medical info only
    """
    
    # Detect trigger words
    detection_result = TriggerWordDetector.detect_trigger(trigger_input.input_text)
    
    if not detection_result["triggered"]:
        return EmergencyTriggerResponse(
            detected=False,
            detection_details=TriggerDetectionResult(**detection_result),
            medical_info=None,
            message="No emergency trigger detected. Please say 'emergency' or 'help' for emergency access."
        )
    
    # Log the trigger detection
    audit_log = AuditLog(
        action="VIEW",  # Using AuditAction enum value
        actor_id=None,  # No user (emergency access)
        actor_role="EMERGENCY",
        resource_type="emergency_trigger",
        resource_id=None,
        description="Emergency trigger word detected",
        audit_metadata={
            "input_text": trigger_input.input_text,
            "detected_words": detection_result["detected_words"],
            "confidence": detection_result["confidence"],
            "location": trigger_input.location
        },
        success=True
    )
    db.add(audit_log)
    
    # Try to find patient
    patient = None
    patient_identifier = trigger_input.patient_identifier
    
    # If no identifier provided, try to extract from text
    if not patient_identifier:
        patient_identifier = TriggerWordDetector.extract_patient_identifier(trigger_input.input_text)
    
    if patient_identifier:
        # Try to find patient by ID, phone, or biometric
        patient = db.query(Patient).filter(
            (Patient.id == patient_identifier) |
            (Patient.phone.contains(patient_identifier))
        ).first()
    
    if not patient:
        db.commit()
        return EmergencyTriggerResponse(
            detected=True,
            detection_details= TriggerDetectionResult(**detection_result),
            medical_info=None,
            message="⚠️ Emergency detected! But no patient identified. Please provide patient ID or phone number."
        )
    
    # Get patient's critical medical information
    patient_data = {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "blood_group": patient.blood_group,
        "emergency_contact": patient.emergency_contact,
        "phone": patient.phone,
    }
    
    # Get allergies
    allergies = db.query(Allergy).filter(
        Allergy.patient_id == patient.id,
        Allergy.is_active == True
    ).all()
    patient_data["allergies"] = [
        {
            "allergen": a.allergen,
            "severity": a.severity,
            "reaction": a.reaction
        }
        for a in allergies
    ]
    
    # Get health conditions
    conditions = db.query(HealthCondition).filter(
        HealthCondition.patient_id == patient.id,
        HealthCondition.is_active == True
    ).all()
    patient_data["health_conditions"] = [
        {
            "condition": c.condition,
            "severity": c.severity,
            "notes": c.notes
        }
        for c in conditions
    ]
    
    # Get latest vitals
    latest_vital = db.query(Vital).filter(
        Vital.patient_id == patient.id
    ).order_by(Vital.recorded_at.desc()).first()
    
    if latest_vital:
        patient_data["latest_vitals"] = {
            "heart_rate": latest_vital.heart_rate,
            "blood_pressure": f"{latest_vital.blood_pressure_systolic}/{latest_vital.blood_pressure_diastolic}" if latest_vital.blood_pressure_systolic else None,
            "temperature": latest_vital.temperature,
            "spo2": latest_vital.spo2,
            "recorded_at": latest_vital.recorded_at.isoformat() if latest_vital.recorded_at else None
        }
    else:
        patient_data["latest_vitals"] = {}
    
    # Placeholder for medications (would need medications table)
    patient_data["medications"] = []
    
    # Format emergency response
    emergency_info_dict = TriggerWordDetector.format_emergency_response(patient_data)
    emergency_info = EmergencyMedicalInfo(**emergency_info_dict)
    
    # Create emergency access record
    emergency_access = EmergencyAccess(
        patient_id=patient.id,
        requested_by=None,  # Triggered automatically
        reason=f"Emergency trigger detected: {', '.join(detection_result['detected_words'])}",
        location=trigger_input.location or "Not provided",
        is_active=True
    )
    db.add(emergency_access)
    
    # Log patient access
    patient_audit = AuditLog(
        action="VIEW",
        actor_id=None,
        actor_role="EMERGENCY",
        resource_type="patient",
        resource_id=patient.id,
        description="Emergency access to patient medical information",
        audit_metadata={
            "trigger_confidence": detection_result["confidence"],
            "detected_words": detection_result["detected_words"],
            "access_type": "EMERGENCY_READ_ONLY"
        },
        success=True
    )
    db.add(patient_audit)
    
    db.commit()
    
    return EmergencyTriggerResponse(
        detected=True,
        detection_details=TriggerDetectionResult(**detection_result),
        medical_info=emergency_info,
        message=f"🚨 EMERGENCY ACCESS GRANTED - Critical medical information for {patient.first_name} {patient.last_name} (READ-ONLY)"
    )


@router.get("/test-detection/{text}")
async def test_trigger_detection(text: str):
    """
    Test trigger word detection without accessing patient data.
    Useful for testing voice recognition systems.
    
    Example: /emergency-trigger/test-detection/emergency%20help
    """
    detection_result = TriggerWordDetector.detect_trigger(text)
    
    return {
        "test_input": text,
        "detection": detection_result,
        "message": "Triggered! Emergency mode would activate." if detection_result["triggered"] else "Not triggered. Try words like 'emergency', 'help', 'urgent'."
    }


@router.get("/trigger-words")
async def get_trigger_words():
    """
    Get list of all trigger words and phrases that activate emergency mode.
    Useful for UI/voice system configuration.
    """
    return {
        "trigger_words": TriggerWordDetector.TRIGGER_WORDS,
        "trigger_phrases": TriggerWordDetector.EMERGENCY_PHRASES,
        "languages_supported": ["English", "Hindi", "Chinese"],
        "note": "Any of these words/phrases will activate emergency read-only access"
    }
