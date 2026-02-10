"""
Emergency Trigger Word Detection Service
Detects trigger words like "emergency" and provides quick access to critical medical information.
"""

import re
from typing import Optional, List
from datetime import datetime


class TriggerWordDetector:
    """Detects emergency trigger words in voice/text input."""
    
    # Define trigger words and variations
    TRIGGER_WORDS = [
        "emergency",
        "help",
        "urgent",
        "critical",
        "救命",  # Chinese for "help"
        "सहायता",  # Hindi for "help"
    ]
    
    # Emergency-related phrases
    EMERGENCY_PHRASES = [
        "need help",
        "medical emergency",
        "heart attack",
        "can't breathe",
        "unconscious",
        "severe pain",
        "accident",
    ]
    
    @classmethod
    def detect_trigger(cls, input_text: str) -> dict:
        """
        Detect trigger words in input text.
        
        Args:
            input_text: Text to analyze (voice-to-text or text input)
            
        Returns:
            dict with detection results
        """
        if not input_text:
            return {
                "triggered": False,
                "confidence": 0.0,
                "detected_words": [],
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Normalize input
        normalized_text = input_text.lower().strip()
        
        detected_words = []
        confidence_score = 0.0
        
        # Check for exact trigger words
        for trigger in cls.TRIGGER_WORDS:
            if trigger.lower() in normalized_text:
                detected_words.append(trigger)
                confidence_score += 0.4
        
        # Check for emergency phrases
        for phrase in cls.EMERGENCY_PHRASES:
            if phrase.lower() in normalized_text:
                detected_words.append(phrase)
                confidence_score += 0.3
        
        # Cap confidence at 1.0
        confidence_score = min(confidence_score, 1.0)
        
        return {
            "triggered": len(detected_words) > 0,
            "confidence": confidence_score,
            "detected_words": detected_words,
            "input_text": input_text,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def extract_patient_identifier(cls, input_text: str) -> Optional[str]:
        """
        Try to extract patient identifier from emergency message.
        Looks for patterns like:
        - "patient ID abc123"
        - "ID: abc123"
        - "for patient abc123"
        
        Args:
            input_text: Text to analyze
            
        Returns:
            Extracted patient ID or None
        """
        if not input_text:
            return None
        
        # Common patterns for patient ID
        patterns = [
            r'patient\s+id\s+([a-zA-Z0-9-]+)',
            r'id[:\s]+([a-zA-Z0-9-]+)',
            r'for\s+patient\s+([a-zA-Z0-9-]+)',
            r'patient\s+([a-zA-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, input_text.lower())
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def format_emergency_response(cls, patient_data: dict) -> dict:
        """
        Format patient data for emergency response (read-only).
        Returns only critical medical information.
        
        Args:
            patient_data: Complete patient data from database
            
        Returns:
            Formatted emergency info (read-only, critical data only)
        """
        # Extract only critical emergency information
        emergency_info = {
            "patient_id": patient_data.get("id"),
            "name": f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}",
            "age": cls._calculate_age(patient_data.get("date_of_birth")),
            "blood_group": patient_data.get("blood_group", "Unknown"),
            "emergency_contact": patient_data.get("emergency_contact", "Not available"),
            "phone": patient_data.get("phone", "Not available"),
            
            # Critical medical info
            "allergies": patient_data.get("allergies", []),
            "conditions": patient_data.get("health_conditions", []),
            "medications": patient_data.get("medications", []),
            
            # Latest vitals (if available)
            "latest_vitals": patient_data.get("latest_vitals", {}),
            
            # Access info
            "access_type": "EMERGENCY_READ_ONLY",
            "access_granted_at": datetime.utcnow().isoformat(),
            "note": "⚠️ EMERGENCY ACCESS - READ ONLY - Critical medical information for emergency responders",
        }
        
        return emergency_info
    
    @staticmethod
    def _calculate_age(date_of_birth: str) -> Optional[int]:
        """Calculate age from date of birth."""
        if not date_of_birth:
            return None
        
        try:
            from datetime import datetime
            if isinstance(date_of_birth, str):
                dob = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
            else:
                dob = date_of_birth
            
            today = datetime.now()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        except:
            return None
