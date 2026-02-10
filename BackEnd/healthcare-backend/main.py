"""
Main FastAPI application.
DigiLocker-style Universal Healthcare Backend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings  
from app.routers import auth, patients, vitals, consent, emergency, health_profile, device_ingest, notes, blood_reports, emergency_trigger

# Import database to ensure models are registered
from app.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Universal Healthcare Backend",
    description="DigiLocker-style healthcare backend with offline-first, biometric identity, and DPDP compliance",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(vitals.router)
app.include_router(consent.router)
app.include_router(emergency.router)
app.include_router(health_profile.router)
app.include_router(device_ingest.router)  # Fault-tolerant device data ingestion
app.include_router(notes.router)  # Clinical notes with role-based encryption
app.include_router(blood_reports.router)  # PDF blood report parsing
app.include_router(emergency_trigger.router)  # Emergency trigger word detection

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Returns system status and configuration.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "features": {
            "offline_first": True,
            "biometric_identity": True,
            "consent_management": True,
            "emergency_access": True,
            "device_integration": True,
            "audit_logging": True,
            "dpdp_compliant": True,
            "encrypted_notes": True,
            "pdf_blood_reports": True,
            "emergency_trigger_detection": True
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Universal Healthcare Backend API",
        "version": "1.0.0",
        "description": "DigiLocker-style healthcare backend",
        "documentation": "/docs" if settings.DEBUG else "disabled in production",
        "health_check": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
