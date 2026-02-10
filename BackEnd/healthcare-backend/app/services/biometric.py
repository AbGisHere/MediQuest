"""
Biometric hashing service.
Provides secure biometric hashing (fingerprint + face) using HMAC-SHA256.
Backend NEVER stores raw biometric data - only hashed templates.
"""
import hashlib
import hmac
from typing import Optional
import os


# Secret key for HMAC (should be in environment variables in production)
BIOMETRIC_SECRET_KEY = os.getenv("BIOMETRIC_SECRET_KEY", "default-secret-key-change-in-production")


def hash_biometric(biometric_data: str, biometric_type: str = "fingerprint") -> str:
    """
    Hash biometric data using HMAC-SHA256.
    
    Args:
        biometric_data: Raw biometric data (fingerprint or face template)
        biometric_type: Type of biometric ("fingerprint" or "face")
        
    Returns:
        HMAC-SHA256 hash of the biometric data
        
    Note:
        - Raw biometric data is NEVER stored
        - Uses keyed hash (HMAC) for additional security
        - Hash is deterministic: same biometric → same hash
        - One-way function: cannot reverse hash to get biometric
    """
    # Add type prefix for additional uniqueness
    data_to_hash = f"{biometric_type}:{biometric_data}"
    
    # Create HMAC-SHA256 hash
    hash_object = hmac.new(
        BIOMETRIC_SECRET_KEY.encode('utf-8'),
        data_to_hash.encode('utf-8'),
        hashlib.sha256
    )
    return hash_object.hexdigest()


def hash_fingerprint(fingerprint_data: str) -> str:
    """
    Hash fingerprint data using HMAC-SHA256.
    
    Args:
        fingerprint_data: Raw fingerprint data (base64 string or template)
        
    Returns:
        HMAC-SHA256 hash of the fingerprint
    """
    return hash_biometric(fingerprint_data, "fingerprint")


def hash_face(face_data: str) -> str:
    """
    Hash face data using HMAC-SHA256.
    
    Args:
        face_data: Raw face data (face template or encoding)
        
    Returns:
        HMAC-SHA256 hash of the face data
    """
    return hash_biometric(face_data, "face")


def verify_biometric(biometric_data: str, stored_hash: str, biometric_type: str = "fingerprint") -> bool:
    """
    Verify biometric data against stored hash.
    
    Args:
        biometric_data: Raw biometric data to verify
        stored_hash: Previously stored biometric hash
        biometric_type: Type of biometric ("fingerprint" or "face")
        
    Returns:
        True if biometric matches, False otherwise
    """
    computed_hash = hash_biometric(biometric_data, biometric_type)
    return hmac.compare_digest(computed_hash, stored_hash)


def verify_fingerprint(fingerprint_data: str, stored_hash: str) -> bool:
    """
    Verify fingerprint against stored hash.
    
    Args:
        fingerprint_data: Raw fingerprint data to verify
        stored_hash: Previously stored fingerprint hash
        
    Returns:
        True if fingerprint matches, False otherwise
    """
    return verify_biometric(fingerprint_data, stored_hash, "fingerprint")


def verify_face(face_data: str, stored_hash: str) -> bool:
    """
    Verify face data against stored hash.
    
    Args:
        face_data: Raw face data to verify
        stored_hash: Previously stored face hash
        
    Returns:
        True if face matches, False otherwise
    """
    return verify_biometric(face_data, stored_hash, "face")


def generate_checksum(data: str) -> str:
    """
    Generate SHA-256 checksum for data integrity.
    Used for offline batch validation.
    
    Args:
        data: Data to checksum
        
    Returns:
        SHA-256 checksum
    """
    hash_object = hashlib.sha256(data.encode('utf-8'))
    return hash_object.hexdigest()

