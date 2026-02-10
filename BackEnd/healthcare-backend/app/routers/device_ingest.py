"""
Device Ingestion Router - Fault-Tolerant Data Collection
Handles data from Raspberry Pi/microcontrollers via phone gateway.
CRITICAL: Must accept partial payloads and never crash on missing data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FaultTolerantDeviceIngest, MedicalTestCreate
from app.models import Device, Vital, MedicalTest, Consent, ConsentPurpose, AuditLog, AuditAction
from app.auth.password import verify_password
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["Device Ingestion"])


def verify_device_api_key(device_id: str, api_key: str, db: Session) -> Device:
    """Verify device authentication."""
    device = db.query(Device).filter(Device.id == device_id, Device.is_active == True).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or inactive")
    
    # Verify API key
    if not verify_password(api_key, device.api_key_hash):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return device


def check_patient_consent(patient_id: str, db: Session) -> bool:
    """Check if patient has granted consent for data collection."""
    consent = db.query(Consent).filter(
        Consent.patient_id == patient_id,
        Consent.purpose == ConsentPurpose.TREATMENT,
        Consent.granted == True,
        Consent.is_active == True
    ).first()
    
    return consent is not None


@router.post("/ingest")
async def ingest_device_data(
    data: FaultTolerantDeviceIngest,
    db: Session = Depends(get_db)
):
    """
    POST /devices/ingest - Fault-tolerant device data ingestion
    
    CRITICAL FEATURES:
    - Accepts partial payloads (missing vitals/tests are OK)
    - Never crashes on missing data
    - Validates device authentication
    - Enforces patient consent
    - Stores available vitals and tests
    - Triggers alerts if needed
    - Logs audit event
    
    Data flow: Sensors → Pi → Phone → Backend
    """
    try:
        # 1. Authenticate device
        device = verify_device_api_key(data.device_id, data.api_key, db)
        logger.info(f"Device {device.device_name} authenticated successfully")
        
        # 2. Enforce patient consent
        if not check_patient_consent(data.patient_id, db):
            logger.warning(f"Consent denied for patient {data.patient_id}")
            raise HTTPException(
                status_code=403,
                detail="Patient has not granted consent for data collection"
            )
        
        # 3. Update device heartbeat
        device.last_heartbeat = datetime.now(timezone.utc)
        
        # 4. Determine timestamp
        recorded_at = data.recorded_at or datetime.now(timezone.utc)
        
        # 5. Store available vitals (FAULT-TOLERANT)
        vitals_stored = []
        vital_mappings = {
            'heart_rate': ('heart_rate', 'bpm'),
            'bp_systolic': ('bp_systolic', 'mmHg'),
            'bp_diastolic': ('bp_diastolic', 'mmHg'),
            'spo2': ('spo2', '%'),
            'temperature': ('temperature', '°F'),
            'glucose': ('glucose', 'mg/dL'),
            'weight': ('weight', 'kg'),
            'height': ('height', 'cm'),
            'bmi': ('bmi', 'kg/m²'),
            'respiratory_rate': ('respiratory_rate', 'bpm'),
            'ecg': ('ecg', 'raw'),
            'steps': ('steps', 'count'),
            'sleep_hours': ('sleep_hours', 'hours'),
            'calories': ('calories', 'kcal'),
        }
        
        for field_name, (vital_type, unit) in vital_mappings.items():
            value = getattr(data, field_name, None)
            if value is not None:  # Only store if present
                try:
                    vital = Vital(
                        id=str(uuid.uuid4()),
                        patient_id=data.patient_id,
                        vital_type=vital_type,
                        value=float(value) if not isinstance(value, str) else 0.0,
                        unit=unit,
                        source="device",
                        source_id=device.id,
                        recorded_at=recorded_at,
                        batch_id=data.batch_id,
                        uploaded_by=None  # Device upload, no user
                    )
                    
                    # Special handling for ECG (string data)
                    if field_name == 'ecg':
                        vital.notes = str(value)
                        vital.value = 0.0  # Placeholder
                    
                    db.add(vital)
                    vitals_stored.append(vital_type)
                except Exception as e:
                    logger.error(f"Error storing vital {vital_type}: {e}")
                    # Continue processing other vitals
        
        # 6. Store medical tests (FAULT-TOLERANT)
        tests_stored = []
        if data.medical_tests:
            for test_data in data.medical_tests:
                try:
                    test = MedicalTest(
                        id=str(uuid.uuid4()),
                        patient_id=data.patient_id,
                        test_type=test_data.test_type,
                        result=test_data.result,
                        numeric_value=test_data.numeric_value,
                        unit=test_data.unit,
                        source=test_data.source,
                        source_id=device.id,
                        performed_at=test_data.performed_at or recorded_at,
                        notes=test_data.notes,
                        batch_id=data.batch_id,
                        uploaded_by=None
                    )
                    db.add(test)
                    tests_stored.append(test_data.test_type)
                except Exception as e:
                    logger.error(f"Error storing test {test_data.test_type}: {e}")
                    # Continue processing other tests
        
        # 7. Trigger alerts if needed
        alerts_generated = []
        try:
            from app.services.alerts import AlertEngine
            for vital in db.query(Vital).filter(Vital.batch_id == data.batch_id).all():
                alert = AlertEngine.evaluate_vital(db, vital)
                if alert:
                    alerts_generated.append(alert.id)
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            # Don't fail ingestion if alert generation fails
        
        # 8. Log audit event
        try:
            audit = AuditLog(
                action=AuditAction.DATA_ACCESS,
                actor_id=device.id,
                actor_role="device",
                resource_type="device_ingestion",
                resource_id=data.patient_id,
                description=f"Device {device.device_name} ingested data: {len(vitals_stored)} vitals, {len(tests_stored)} tests",
                success=True,
                ip_address=None
            )
            db.add(audit)
        except Exception as e:
            logger.error(f"Error logging audit: {e}")
        
        # 9. Commit all changes
        db.commit()
        
        return {
            "success": True,
            "message": "Data ingested successfully",
            "patient_id": data.patient_id,
            "device_id": device.id,
            "vitals_stored": vitals_stored,
            "tests_stored": tests_stored,
            "alerts_generated": alerts_generated,
            "timestamp": recorded_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in device ingestion: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during data ingestion: {str(e)}"
        )


@router.get("/ingest/health")
async def ingestion_health_check():
    """Health check for device ingestion endpoint."""
    return {
        "status": "healthy",
        "endpoint": "/devices/ingest",
        "features": {
            "fault_tolerant": True,
            "partial_payloads": True,
            "consent_enforcement": True,
            "alert_generation": True,
            "audit_logging": True
        }
    }
