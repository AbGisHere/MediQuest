"""
Alert engine service.
Automatically generates alerts based on vital values and rules.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.alert import Alert, AlertType, AlertSeverity
from app.models.vitals import Vital, VitalType


class AlertEngine:
    """
    Rule-based alert generation engine.
    Evaluates vital values against thresholds and generates alerts.
    """
    
    # Alert rules: {vital_type: [(condition, alert_type, severity, title, description_template)]}
    ALERT_RULES = {
        VitalType.GLUCOSE: [
            (
                lambda v: v > 300,
                AlertType.DIABETES_HIGH,
                AlertSeverity.CRITICAL,
                "Critical High Blood Glucose",
                "Blood glucose level of {value} mg/dL is critically high. Immediate action required."
            ),
            (
                lambda v: v > 180,
                AlertType.DIABETES_HIGH,
                AlertSeverity.HIGH,
                "High Blood Glucose",
                "Blood glucose level of {value} mg/dL is above normal range."
            ),
            (
                lambda v: v < 70,
                AlertType.DIABETES_LOW,
                AlertSeverity.HIGH,
                "Low Blood Glucose",
                "Blood glucose level of {value} mg/dL is below normal range."
            ),
            (
                lambda v: v < 54,
                AlertType.DIABETES_LOW,
                AlertSeverity.CRITICAL,
                "Critical Low Blood Glucose",
                "Blood glucose level of {value} mg/dL is critically low. Immediate action required."
            ),
        ],
        VitalType.HEART_RATE: [
            (
                lambda v: v > 120,
                AlertType.ABNORMAL_HEART_RATE,
                AlertSeverity.HIGH,
                "High Heart Rate",
                "Heart rate of {value} bpm is elevated."
            ),
            (
                lambda v: v < 50,
                AlertType.ABNORMAL_HEART_RATE,
                AlertSeverity.HIGH,
                "Low Heart Rate",
                "Heart rate of {value} bpm is below normal range."
            ),
        ],
        VitalType.OXYGEN_SATURATION: [
            (
                lambda v: v < 90,
                AlertType.LOW_OXYGEN,
                AlertSeverity.CRITICAL,
                "Critical Low Oxygen Saturation",
                "Oxygen saturation of {value}% is critically low."
            ),
            (
                lambda v: v < 95,
                AlertType.LOW_OXYGEN,
                AlertSeverity.HIGH,
                "Low Oxygen Saturation",
                "Oxygen saturation of {value}% is below normal range."
            ),
        ],
        VitalType.BLOOD_PRESSURE_SYSTOLIC: [
            (
                lambda v: v > 180,
                AlertType.HIGH_BLOOD_PRESSURE,
                AlertSeverity.CRITICAL,
                "Critical High Blood Pressure",
                "Systolic blood pressure of {value} mmHg is critically high."
            ),
            (
                lambda v: v > 140,
                AlertType.HIGH_BLOOD_PRESSURE,
                AlertSeverity.MEDIUM,
                "High Blood Pressure",
                "Systolic blood pressure of {value} mmHg is elevated."
            ),
            (
                lambda v: v < 90,
                AlertType.LOW_BLOOD_PRESSURE,
                AlertSeverity.MEDIUM,
                "Low Blood Pressure",
                "Systolic blood pressure of {value} mmHg is low."
            ),
        ],
        VitalType.TEMPERATURE: [
            (
                lambda v: v > 39.4,  # 103°F
                AlertType.ABNORMAL_TEMPERATURE,
                AlertSeverity.HIGH,
                "High Fever",
                "Body temperature of {value}°C indicates high fever."
            ),
            (
                lambda v: v > 38.0,  # 100.4°F
                AlertType.ABNORMAL_TEMPERATURE,
                AlertSeverity.MEDIUM,
                "Fever",
                "Body temperature of {value}°C is above normal."
            ),
            (
                lambda v: v < 35.0,  # 95°F
                AlertType.ABNORMAL_TEMPERATURE,
                AlertSeverity.HIGH,
                "Hypothermia",
                "Body temperature of {value}°C is abnormally low."
            ),
        ],
    }
    
    @staticmethod
    def evaluate_vital(db: Session, vital: Vital) -> Optional[Alert]:
        """
        Evaluate a vital and generate alert if necessary.
        
        Args:
            db: Database session
            vital: Vital to evaluate
            
        Returns:
            Generated Alert if rule triggered, None otherwise
        """
        # Get rules for this vital type
        rules = AlertEngine.ALERT_RULES.get(vital.vital_type)
        if not rules:
            return None
        
        # Evaluate each rule
        for condition, alert_type, severity, title, description_template in rules:
            if condition(vital.value):
                # Create alert
                alert = Alert(
                    patient_id=vital.patient_id,
                    alert_type=alert_type,
                    severity=severity,
                    title=title,
                    description=description_template.format(value=vital.value),
                    vital_id=vital.id,
                    trigger_value=vital.value
                )
                
                db.add(alert)
                db.commit()
                db.refresh(alert)
                
                return alert
        
        return None
    
    @staticmethod
    def evaluate_batch(db: Session, vitals: List[Vital]) -> List[Alert]:
        """
        Evaluate multiple vitals and generate alerts.
        
        Args:
            db: Database session
            vitals: List of vitals to evaluate
            
        Returns:
            List of generated alerts
        """
        alerts = []
        for vital in vitals:
            alert = AlertEngine.evaluate_vital(db, vital)
            if alert:
                alerts.append(alert)
        
        return alerts
