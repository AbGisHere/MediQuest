"""
Configuration management for the healthcare backend.
Loads settings from environment variables with validation.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_API: str = "60/minute"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Emergency Access
    EMERGENCY_ACCESS_DURATION_HOURS: int = 2
    
    # Data Retention (days)
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    VITAL_DATA_RETENTION_DAYS: int = 3650  # 10 years
    ALERT_RETENTION_DAYS: int = 365
    
    # Encryption
    ENCRYPTION_KEY: str
    
    # Biometric Security
    BIOMETRIC_SECRET_KEY: str = "default-biometric-key-change-in-production-min-32-chars"
    
    # Role-Based Encryption Keys (for clinical notes)
    DOCTOR_ENCRYPTION_KEY: str = "default-doctor-encryption-key-change-in-production-min-32-chars"
    PATIENT_ENCRYPTION_KEY: str = "default-patient-encryption-key-change-in-production-min-32-chars"
    ADMIN_ENCRYPTION_KEY: str = "default-admin-encryption-key-change-in-production-min-32-chars"
    
    # File Upload Configuration
    UPLOAD_DIR: str = "./uploads/blood_reports"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"


# Global settings instance
settings = Settings()
