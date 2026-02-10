"""
Blood Reports Router
Handles PDF upload and parsing of blood test reports.

Access Rules:
- Admin: Can upload PDFs for any patient
- Doctor: Can view reports
- Patient: Can view own reports
"""
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database import get_db
from app.models.user import User
from app.models.patient import Patient  
from app.models.blood_report import BloodReport, ReportType
from app.schemas import BloodReportResponse, BloodReportSummary
from app.services.pdf_parser import PDFParser
from app.routers.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/blood-reports", tags=["Blood Reports"])


# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=BloodReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_blood_report(
    patient_id: str = Form(...),
    test_date: Optional[str] = Form(None),
    lab_name: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a blood test report PDF (Admin only).
    
    The PDF will be parsed automatically and medical values extracted.
    """
    # Only admins can upload PDFs
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can upload blood reports"
        )
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning
    
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Generate unique filename
    import uuid
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Parse PDF
    try:
        extracted_values, full_text, report_type, confidence = PDFParser.parse_blood_report(file_path)
        file_hash = PDFParser.calculate_file_hash(file_path)
    except Exception as e:
        # Clean up file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse PDF: {str(e)}"
        )
    
    # Parse test date if provided
    parsed_test_date = None
    if test_date:
        try:
            parsed_test_date = datetime.strptime(test_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    # Create blood report record
    blood_report = BloodReport(
        patient_id=patient_id,
        uploaded_by=current_user.id,
        report_type=report_type,
        test_date=parsed_test_date,
        lab_name=lab_name,
        pdf_file_path=file_path,
        pdf_file_hash=file_hash,
        pdf_file_size=file_size / (1024 * 1024),  # Convert to MB
        extracted_text=full_text[:10000],  # Limit text storage
        parsing_confidence=confidence,
        **extracted_values  # Unpack all extracted values
    )
    
    db.add(blood_report)
    db.commit()
    db.refresh(blood_report)
    
    return BloodReportResponse(
        id=blood_report.id,
        patient_id=blood_report.patient_id,
        uploaded_by=blood_report.uploaded_by,
        uploader_name=current_user.username,
        report_type=blood_report.report_type.value,
        test_date=blood_report.test_date,
        lab_name=blood_report.lab_name,
        hemoglobin=blood_report.hemoglobin,
        wbc_count=blood_report.wbc_count,
        rbc_count=blood_report.rbc_count,
        platelet_count=blood_report.platelet_count,
        glucose_fasting=blood_report.glucose_fasting,
        glucose_random=blood_report.glucose_random,
        cholesterol_total=blood_report.cholesterol_total,
        cholesterol_hdl=blood_report.cholesterol_hdl,
        cholesterol_ldl=blood_report.cholesterol_ldl,
        triglycerides=blood_report.triglycerides,
        sgot=blood_report.sgot,
        sgpt=blood_report.sgpt,
        creatinine=blood_report.creatinine,
        urea=blood_report.urea,
        parsing_confidence=blood_report.parsing_confidence,
        uploaded_at=blood_report.uploaded_at
    )


@router.get("/patient/{patient_id}", response_model=List[BloodReportSummary])
def get_patient_reports(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all blood reports for a patient.
    
    Access: Doctor, Admin, or patient themselves
    """
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Access control
    if current_user.role.value == "PATIENT":
        # Patients can only view their own reports
        # TODO: Implement patient-user linking
        pass
    elif current_user.role.value == "doctor":
        # Doctors need consent to access patient blood reports
        from app.services.consent import ConsentService
        from app.models.consent import ConsentPurpose
        
        has_consent = ConsentService.check_consent(
            db=db,
            patient_id=patient_id,
            purpose=ConsentPurpose.TREATMENT,
            doctor_id=current_user.id
        )
        
        if not has_consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No consent granted for blood report access"
            )
    elif current_user.role.value == "admin":
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    reports = db.query(BloodReport).filter(
        BloodReport.patient_id == patient_id
    ).order_by(BloodReport.uploaded_at.desc()).all()
    
    return [
        BloodReportSummary(
            id=report.id,
            patient_id=report.patient_id,
            report_type=report.report_type.value,
            test_date=report.test_date,
            lab_name=report.lab_name,
            parsing_confidence=report.parsing_confidence,
            uploaded_at=report.uploaded_at
        )
        for report in reports
    ]


@router.get("/{report_id}", response_model=BloodReportResponse)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed blood report with all values.
    
    Access: Doctor, Admin, or patient themselves
    """
    report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Access control
    if current_user.role.value == "PATIENT":
        # TODO: Check if this patient owns the report
        pass
    elif current_user.role.value == "doctor":
        # Doctors need consent to access patient blood reports
        from app.services.consent import ConsentService
        from app.models.consent import ConsentPurpose
        
        has_consent = ConsentService.check_consent(
            db=db,
            patient_id=report.patient_id,
            purpose=ConsentPurpose.TREATMENT,
            doctor_id=current_user.id
        )
        
        if not has_consent:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No consent granted for blood report access"
            )
    elif current_user.role.value == "admin":
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get uploader name
    uploader = db.query(User).filter(User.id == report.uploaded_by).first()
    uploader_name = uploader.username if uploader else "Unknown"
    
    return BloodReportResponse(
        id=report.id,
        patient_id=report.patient_id,
        uploaded_by=report.uploaded_by,
        uploader_name=uploader_name,
        report_type=report.report_type.value,
        test_date=report.test_date,
        lab_name=report.lab_name,
        hemoglobin=report.hemoglobin,
        wbc_count=report.wbc_count,
        rbc_count=report.rbc_count,
        platelet_count=report.platelet_count,
        glucose_fasting=report.glucose_fasting,
        glucose_random=report.glucose_random,
        cholesterol_total=report.cholesterol_total,
        cholesterol_hdl=report.cholesterol_hdl,
        cholesterol_ldl=report.cholesterol_ldl,
        triglycerides=report.triglycerides,
        sgot=report.sgot,
        sgpt=report.sgpt,
        creatinine=report.creatinine,
        urea=report.urea,
        parsing_confidence=report.parsing_confidence,
        uploaded_at=report.uploaded_at
    )


@router.get("/{report_id}/pdf")
def download_pdf(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download the original PDF file.
    
    Access: Doctor, Admin, or patient themselves
    """
    report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Access control
    if current_user.role.value not in ["DOCTOR", "ADMIN", "PATIENT"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if file exists
    if not os.path.exists(report.pdf_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found on server"
        )
    
    return FileResponse(
        path=report.pdf_file_path,
        media_type="application/pdf",
        filename=f"blood_report_{report_id}.pdf"
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a blood report and its PDF file.
    
    Access: Admin only
    """
    # Only admins can delete reports
    if current_user.role.value != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete reports"
        )
    
    report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete PDF file
    if os.path.exists(report.pdf_file_path):
        try:
            os.remove(report.pdf_file_path)
        except Exception as e:
            print(f"Failed to delete PDF file: {e}")
    
    # Delete database record
    db.delete(report)
    db.commit()
    
    return None
