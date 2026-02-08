"""
Biometric hashing service.
Provides secure fingerprint hashing using SHA-256.
"""
import hashlib
from typing import Optional


def hash_fingerprint(fingerprint_data: str) -> str:
    """
    Hash fingerprint data using SHA-256.
    
    Args:
        fingerprint_data: Raw fingerprint data (base64 string or similar)
        
    Returns:
        SHA-256 hash of the fingerprint
        
    Note:
        - Raw biometric data is NEVER stored
        - Hash is deterministic: same fingerprint → same hash
        - One-way function: cannot reverse hash to get fingerprint
    """
    # Create SHA-256 hash
    hash_object = hashlib.sha256(fingerprint_data.encode('utf-8'))
    return hash_object.hexdigest()


def verify_fingerprint(fingerprint_data: str, stored_hash: str) -> bool:
    """
    Verify fingerprint against stored hash.
    
    Args:
        fingerprint_data: Raw fingerprint data to verify
        stored_hash: Previously stored fingerprint hash
        
    Returns:
        True if fingerprint matches, False otherwise
    """
    computed_hash = hash_fingerprint(fingerprint_data)
    return computed_hash == stored_hash


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
