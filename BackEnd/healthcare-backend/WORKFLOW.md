# 🔄 Universal Healthcare System - Complete Workflow

## Overview
This document describes the complete end-to-end workflow of the Universal Healthcare Backend system, from patient registration to continuous health monitoring.

---

## 🎯 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND                                  │
│  (React/Next.js - Mobile & Web)                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST API (JWT Auth)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND - FastAPI                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Auth System  │  │ Notes System │  │ PDF Parser   │          │
│  │  (JWT)       │  │ (Encrypted)  │  │ (Blood Rpt)  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │ SQLAlchemy ORM
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE - SQLite/PostgreSQL                  │
│  ├─ users            ├─ clinical_notes (encrypted)              │
│  ├─ patients         ├─ blood_reports                           │
│  ├─ vitals           ├─ devices                                 │
│  └─ consents         └─ audit_logs                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Complete User Workflows

### **Workflow 1: Patient Registration & Biometric Setup**

```
1. Patient Registration
   ├─→ POST /patients/register
   │   └─→ Input: name, DOB, gender, contact
   │   └─→ Output: patient_id
   │
2. Biometric Enrollment
   ├─→ Capture fingerprint OR face biometric
   │   └─→ Frontend captures raw biometric
   │   └─→ Backend hashes with HMAC-SHA256
   │   └─→ Stored as BiometricHash (never raw data)
   │
3. Consent Collection
   ├─→ POST /consent/grant
   │   └─→ Purpose: data_collection, emergency_access, research
   │   └─→ DPDP compliant consent management
   │
4. Health Profile Setup
   ├─→ POST /health-profile/conditions
   ├─→ POST /health-profile/allergies
   └─→ Initial health data captured
```

**Example API Call:**
```bash
# Register patient
curl -X POST http://localhost:8000/patients/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "phone": "+91-9876543210",
    "fingerprint_data": "base64_encoded_fingerprint"
  }'
```

---

### **Workflow 2: Doctor Visit & Clinical Notes**

```
1. Doctor Login
   ├─→ POST /auth/login
   │   └─→ username: dr_smith
   │   └─→ password: Doctor@123
   │   └─→ Returns: JWT token
   │
2. Patient Lookup
   ├─→ GET /patients/
   │   └─→ Search for patient
   │   └─→ Verify biometric if needed
   │
3. Review Patient History
   ├─→ GET /vitals/{patient_id}
   ├─→ GET /blood-reports/patient/{patient_id}
   ├─→ GET /notes/patient/{patient_id}
   │
4. Add Clinical Note
   ├─→ POST /notes
   │   └─→ Content: "Patient shows improvement..."
   │   └─→ Encrypted with DOCTOR_KEY
   │   └─→ Category: treatment/diagnosis/prescription
   │
5. Record Vitals
   ├─→ POST /vitals/
   │   └─→ HR, BP, temp, SpO2, glucose
   │   └─→ Alerts triggered if abnormal
```

**Example: Adding a Clinical Note**
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr_smith","password":"Doctor@123"}' \
  | jq -r '.access_token')

# Create note
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "content": "Patient responding well to treatment. BP normalized. Continue current medication.",
    "category": "treatment",
    "is_sensitive": false
  }'
```

---

### **Workflow 3: Admin Uploads Blood Report PDF**

```
1. Admin Login
   ├─→ POST /auth/login
   │   └─→ username: admin
   │   └─→ password: Admin@123
   │
2. Upload PDF Report
   ├─→ POST /blood-reports/upload
   │   └─→ Select patient
   │   └─→ Upload PDF file
   │   └─→ Add metadata (test_date, lab_name)
   │
3. Automatic PDF Parsing
   ├─→ Extract text from PDF
   ├─→ Pattern matching for 30+ values:
   │   ├─ Hemoglobin, WBC, RBC, Platelets
   │   ├─ Glucose, HbA1c
   │   ├─ Cholesterol, Triglycerides
   │   ├─ SGOT, SGPT, Creatinine
   │   └─ TSH, T3, T4
   │
4. Store Results
   ├─→ Structured data in database
   ├─→ Original PDF saved
   └─→ Confidence score calculated
```

**Example: Upload Blood Report**
```bash
# Upload PDF
curl -X POST http://localhost:8000/blood-reports/upload \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "patient_id=patient-uuid" \
  -F "test_date=2026-02-08" \
  -F "lab_name=City Hospital Lab" \
  -F "file=@/path/to/blood_report.pdf"

# Response
{
  "id": "report-uuid",
  "patient_id": "patient-uuid",
  "report_type": "cbc",
  "hemoglobin": 14.5,
  "wbc_count": 7500,
  "rbc_count": 4.8,
  "glucose_fasting": 95,
  "parsing_confidence": 85.5
}
```

---

### **Workflow 4: Device Data Ingestion (Wearable/IoT)**

```
1. Device Registration
   ├─→ Device paired with patient
   │   └─→ Device authentication
   │
2. Continuous Data Collection
   ├─→ POST /devices/ingest
   │   └─→ Fault-tolerant: accepts partial data
   │   └─→ {
   │       "patient_id": "uuid",
   │       "device_id": "smartwatch-001",
   │       "heart_rate": 72,
   │       "blood_pressure_systolic": 120,
   │       "spo2": 98,
   │       "steps": 5000
   │     }
   │
3. Real-Time Processing
   ├─→ Consent verification
   ├─→ Threshold checking
   ├─→ Alert generation if abnormal
   │   └─→ Example: HR > 120 → High alert
   │
4. Audit Logging
   └─→ All data access logged for DPDP compliance
```

---

### **Workflow 5: Patient Views Own Data**

```
1. Patient Login (Mobile App)
   ├─→ Biometric authentication
   │   └─→ POST /patients/verify-biometric
   │
2. View Health Dashboard
   ├─→ GET /vitals/{patient_id}
   ├─→ GET /blood-reports/patient/{patient_id}
   ├─→ GET /notes/patient/{patient_id}
   │   └─→ Notes decrypted with PATIENT_KEY (read-only)
   │
3. Download Reports
   └─→ GET /blood-reports/{report_id}/pdf
       └─→ Download original PDF
```

---

### **Workflow 6: Emergency Access**

```
1. Emergency Trigger
   ├─→ POST /emergency/trigger
   │   └─→ Ambulance/ER staff request access
   │   └─→ Requires: location, reason
   │
2. Temporary Access Granted
   ├─→ System grants 24-hour access
   ├─→ Patient notified (if possible)
   ├─→ Full audit trail created
   │
3. Access Patient Data
   ├─→ GET /emergency/access/{patient_id}
   │   └─→ Returns: vitals, conditions, allergies, medications
   │   └─→ Critical for emergency treatment
   │
4. Terminate Access
   └─→ POST /emergency/terminate/{emergency_access_id}
       └─→ Revoke access after emergency
```

---

## 🔐 Role-Based Access Control

### **Doctor:**
- ✅ **CAN:** Add notes, view patient data, record vitals
- ❌ **CANNOT:** Edit notes, delete data, upload PDFs

### **Patient:**
- ✅ **CAN:** View own data, download reports
- ❌ **CANNOT:** Edit notes, view other patients' data

### **Admin:**
- ✅ **CAN:** Full CRUD on all data, upload PDFs, edit notes
- ✅ **CAN:** Manage users, grant/revoke access

---

## 🔄 Data Flow Diagram

```
Patient Registration
       │
       ├─→ Biometric Enrollment (HMAC hashed)
       │
       ├─→ Consent Collection (DPDP)
       │
       ▼
Continuous Monitoring
       │
       ├─→ Wearable Devices → POST /devices/ingest
       │                        ├─→ Vitals Storage
       │                        └─→ Alert Generation
       │
       ├─→ Doctor Visits → POST /vitals
       │                   POST /notes (encrypted)
       │
       ├─→ Lab Reports → POST /blood-reports/upload (Admin)
       │                 └─→ PDF Parsing (30+ values)
       │
       ▼
Analytics & Alerts
       │
       ├─→ Threshold Monitoring
       ├─→ Alert Generation
       └─→ Notifications
       
       ▼
Patient Access (Read-Only)
       └─→ View encrypted notes
           Download reports
           Track vitals
```

---

## 🎯 Key Features in Workflow

### **1. Biometric Security**
- Never stores raw biometric data
- HMAC-SHA256 hashing
- Timing-attack resistant comparison

### **2. Encrypted Notes**
- AES-256-GCM encryption
- 3 separate keys (Doctor, Patient, Admin)
- Role-based decryption

### **3. PDF Parsing**
- Automatic extraction of 30+ medical values
- Report type detection
- Confidence scoring
- Original PDF preservation

### **4. Fault-Tolerant Ingestion**
- Accepts partial device data
- Continues processing despite missing fields
- Comprehensive audit logging

### **5. DPDP Compliance**
- Consent management
- Data minimization
- Audit trails
- Right to access/delete

---

## 🚀 Implementation Timeline

```
Phase 1: Patient Registration (Week 1)
└─→ User management, biometric enrollment, consent

Phase 2: Clinical Data (Week 2)
└─→ Vitals, notes, health profiles

Phase 3: Advanced Features (Week 3-4)
└─→ PDF parsing, device ingestion, emergency access

Phase 4: Security & Compliance (Week 5)
└─→ Encryption, audit logs, DPDP compliance

Phase 5: Testing & Deployment (Week 6)
└─→ End-to-end testing, production deployment
```

---

## 📊 Workflow Summary

| Step | API Endpoint | User Role | Encryption | DPDP |
|------|--------------|-----------|------------|------|
| Register | POST /patients/register | Any | Biometric | ✅ Consent |
| Login | POST /auth/login | All | JWT | ✅ Auth |
| Add Note | POST /notes | Doctor/Admin | AES-256-GCM | ✅ Audit |
| Upload PDF | POST /blood-reports/upload | Admin | File hash | ✅ Audit |
| Ingest Data | POST /devices/ingest | Device | TLS | ✅ Consent |
| View Data | GET endpoints | Role-based | Decrypted | ✅ Access Log |
| Emergency | POST /emergency/trigger | EMT | Temporary | ✅ Logged |

---

**System Status:** ✅ Fully Operational  
**Workflows:** ✅ All Implemented  
**Security:** ✅ Enterprise-Grade  
**Compliance:** ✅ DPDP Ready
