"""
Notes Encryption Service
Provides role-based encryption/decryption for clinical notes.
Uses AES-256-GCM with separate keys for each role.
"""
import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import settings


class NotesEncryption:
    """
    Handles encryption and decryption of clinical notes.
    Uses AES-256-GCM for authenticated encryption.
    Separate keys for DOCTOR, PATIENT, and ADMIN roles.
    """
    
    @staticmethod
    def _derive_key(password: str, salt: bytes = b'healthcare_salt_2026') -> bytes:
        """
        Derive a 32-byte encryption key from a password using PBKDF2HMAC.
        
        Args:
            password: The password/key from settings
            salt: Salt for key derivation
            
        Returns:
            32-byte encryption key
        """
        from cryptography.hazmat.backends import default_backend
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())
    
    @staticmethod
    def encrypt_note(content: str, role: str) -> str:
        """
        Encrypt note content with role-specific key.
        
        Args:
            content: Plain text note content
            role: "doctor", "admin", or "patient"
            
        Returns:
            Base64-encoded encrypted content with nonce
        """
        # Get the appropriate key based on role
        if role.lower() == "doctor":
            key_password = settings.DOCTOR_ENCRYPTION_KEY
        elif role.lower() == "admin":
            key_password = settings.ADMIN_ENCRYPTION_KEY
        elif role.lower() == "patient":
            key_password = settings.PATIENT_ENCRYPTION_KEY
        else:
            raise ValueError(f"Invalid role: {role}")
        
        # Derive encryption key
        key = NotesEncryption._derive_key(key_password)
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Generate random nonce (12 bytes is standard for GCM)
        nonce = os.urandom(12)
        
        # Encrypt the content
        ciphertext = aesgcm.encrypt(nonce, content.encode(), None)
        
        # Combine nonce + ciphertext and encode to base64
        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode()
    
    @staticmethod
    def decrypt_note(encrypted_content: str, role: str) -> str:
        """
        Decrypt note content with role-specific key.
        
        Args:
            encrypted_content: Base64-encoded encrypted content
            role: "doctor", "admin", or "patient"
            
        Returns:
            Decrypted plain text content
        """
        # Get the appropriate key based on role
        if role.lower() == "doctor":
            key_password = settings.DOCTOR_ENCRYPTION_KEY
        elif role.lower() == "admin":
            key_password = settings.ADMIN_ENCRYPTION_KEY
        elif role.lower() == "patient":
            key_password = settings.PATIENT_ENCRYPTION_KEY
        else:
            raise ValueError(f"Invalid role: {role}")
        
        # Derive decryption key
        key = NotesEncryption._derive_key(key_password)
        
        # Create AESGCM cipher
        aesgcm = AESGCM(key)
        
        # Decode from base64
        encrypted_data = base64.b64decode(encrypted_content.encode())
        
        # Extract nonce (first 12 bytes) and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        
        # Decrypt
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
    
    @staticmethod
    def can_decrypt(user_role: str, note_encryption_role: str) -> bool:
        """
        Check if a user with given role can decrypt a note.
        
        Rules:
        - Doctor can decrypt DOCTOR notes
        - Patient can decrypt PATIENT notes (view-only access)
        - Admin can decrypt ALL notes
        
        Args:
            user_role: Role of the user trying to access ("DOCTOR", "PATIENT", "ADMIN")
            note_encryption_role: Role used to encrypt the note
            
        Returns:
            True if user can decrypt, False otherwise
        """
        user_role = user_role.upper()
        note_encryption_role = note_encryption_role.upper()
        
        # Admin can decrypt everything
        if user_role == "ADMIN":
            return True
        
        # Doctor can decrypt doctor notes
        if user_role == "DOCTOR" and note_encryption_role == "DOCTOR":
            return True
        
        # Patient can decrypt patient notes (but notes are typically not encrypted with patient key)
        if user_role == "PATIENT" and note_encryption_role == "PATIENT":
            return True
        
        return False
