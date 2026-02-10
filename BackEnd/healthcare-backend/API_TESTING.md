# 🧪 API Testing Guide

## Complete guide to testing all backend endpoints

---

## 🚀 Quick Start

### **1. Start the Server**
```bash
cd /Users/arshpreetdhillon/Documents/JOHN\ HOPKINS\ copy/healthcare-backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### **2. Access API Documentation**
```
http://localhost:8000/docs
```

### **3. Test Health Check**
```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0",
  "features": {
    "offline_first": true,
    "biometric_identity": true,
    "consent_management": true,
    "emergency_access": true,
    "device_integration": true,
    "audit_logging": true,
    "dpdp_compliant": true,
    "encrypted_notes": true,
    "pdf_blood_reports": true
  }
}
```

---

## 🔑 Test Credentials

### **Users:**
| Username | Password | Role |
|----------|----------|------|
| `admin` | `Admin@123` | ADMIN |
| `dr_smith` | `Doctor@123` | DOCTOR |
| `dr_jones` | `Doctor@123` | DOCTOR |

---

## 📋 API Endpoint Testing

### **1. Authentication Endpoints**

#### **Login (Doctor)**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "password": "Doctor@123"
  }'
```

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": "user-uuid",
  "role": "DOCTOR"
}
```

#### **Store Token for Subsequent Requests**
```bash
# Extract token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr_smith","password":"Doctor@123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo $TOKEN
```

#### **Login (Admin)**
```bash
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

---

### **2. Patient Endpoints**

#### **Register Patient**
```bash
curl -X POST http://localhost:8000/patients/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Patient",
    "date_of_birth": "1995-05-15",
    "gender": "male",
    "phone": "+91-9999999999",
    "email": "test@example.com",
    "fingerprint_data": "test_fingerprint_data_base64"
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "patient-uuid",
  "first_name": "Test",
  "last_name": "Patient",
  "date_of_birth": "1995-05-15",
  "gender": "male",
  "phone": "+91-9999999999",
  "biometric_enrolled": true,
  "created_at": "2026-02-10T18:00:00Z"
}
```

#### **Get All Patients**
```bash
curl -X GET http://localhost:8000/patients/ \
  -H "Authorization: Bearer $TOKEN"
```

#### **Get Specific Patient**
```bash
curl -X GET http://localhost:8000/patients/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Verify Biometric**
```bash
curl -X POST http://localhost:8000/patients/verify-biometric \
  -H "Content-Type: application/json" \
  -d '{
    "fingerprint_data": "test_fingerprint_data_base64"
  }'
```

---

### **3. Clinical Notes Endpoints** ⭐ NEW

#### **Create Clinical Note (Doctor)**
 ```bash
curl -X POST http://localhost:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "content": "Patient showing good progress. BP: 120/80, HR: 72. Continue current medication for 2 more weeks.",
    "category": "treatment",
    "is_sensitive": false
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": "note-uuid",
  "patient_id": "patient-uuid",
  "author_id": "doctor-uuid",
  "author_name": "dr_smith",
  "content": "Patient showing good progress...",  // Decrypted
  "category": "treatment",
  "is_sensitive": false,
  "encryption_role": "doctor",
  "created_at": "2026-02-10T18:00:00Z",
  "updated_at": "2026-02-10T18:00:00Z"
}
```

#### **Get Patient Notes**
```bash
curl -X GET http://localhost:8000/notes/patient/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Get Specific Note**
```bash
curl -X GET http://localhost:8000/notes/{note_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Update Note (Admin Only)**
```bash
curl -X PUT http://localhost:8000/notes/{note_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated note content",
    "category": "diagnosis"
  }'
```

#### **Delete Note (Admin Only)**
```bash
curl -X DELETE http://localhost:8000/notes/{note_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### **4. Blood Reports Endpoints** ⭐ NEW

#### **Upload PDF Blood Report (Admin Only)**
```bash
curl -X POST http://localhost:8000/blood-reports/upload \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -F "patient_id=patient-uuid" \
  -F "test_date=2026-02-08" \
  -F "lab_name=City Hospital Laboratory" \
  -F "file=@/path/to/blood_report.pdf"
```

**Expected Response (201 Created):**
```json
{
  "id": "report-uuid",
  "patient_id": "patient-uuid",
  "uploaded_by": "admin-uuid",
  "uploader_name": "admin",
  "report_type": "cbc",
  "test_date": "2026-02-08",
  "lab_name": "City Hospital Laboratory",
  "hemoglobin": 14.5,
  "wbc_count": 7500,
  "rbc_count": 4.8,
  "platelet_count": 250000,
  "glucose_fasting": 95,
  "cholesterol_total": 180,
  "parsing_confidence": 85.5,
  "uploaded_at": "2026-02-10T18:00:00Z"
}
```

#### **Get Patient Blood Reports**
```bash
curl -X GET http://localhost:8000/blood-reports/patient/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Get Specific Blood Report**
```bash
curl -X GET http://localhost:8000/blood-reports/{report_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Download PDF**
```bash
curl -X GET http://localhost:8000/blood-reports/{report_id}/pdf \
  -H "Authorization: Bearer $TOKEN" \
  --output blood_report.pdf
```

#### **Delete Blood Report (Admin Only)**
```bash
curl -X DELETE http://localhost:8000/blood-reports/{report_id} \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

### **5. Vitals Endpoints**

#### **Record Vitals**
```bash
curl -X POST http://localhost:8000/vitals/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "heart_rate": 72,
    "blood_pressure_systolic": 120,
    "blood_pressure_diastolic": 80,
    "temperature": 98.6,
    "spo2": 98,
    "respiratory_rate": 16,
    "glucose": 95
  }'
```

#### **Get Patient Vitals**
```bash
curl -X GET "http://localhost:8000/vitals/{patient_id}?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### **Batch Record Vitals**
```bash
curl -X POST http://localhost:8000/vitals/batch \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vitals": [
      {
        "patient_id": "patient-uuid",
        "heart_rate": 72,
        "spo2": 98
      },
      {
        "patient_id": "patient-uuid",
        "heart_rate": 75,
        "spo2": 97
      }
    ]
  }'
```

---

### **6. Device Ingestion Endpoints**

#### **Health Check**
```bash
curl -X GET http://localhost:8000/devices/ingest/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "endpoint": "/devices/ingest",
  "features": {
    "fault_tolerant": true,
    "partial_payloads": true,
    "consent_enforcement": true,
    "alert_generation": true,
    "audit_logging": true
  }
}
```

#### **Ingest Device Data (Fault-Tolerant)**
```bash
curl -X POST http://localhost:8000/devices/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "device_id": "smartwatch-001",
    "device_type": "wearable",
    "consent_verified": true,
    "heart_rate": 72,
    "spo2": 98,
    "steps": 5000,
    "sleep_hours": 7.5
  }'
```

**Note:** This endpoint accepts partial data. Missing fields are OK.

---

### **7. Consent Endpoints**

#### **Grant Consent**
```bash
curl -X POST http://localhost:8000/consent/grant \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "purpose": "data_collection",
    "granted_by": "user-uuid"
  }'
```

#### **Check Consent**
```bash
curl -X GET "http://localhost:8000/consent/{patient_id}/check/data_collection" \
  -H "Authorization: Bearer $TOKEN"
```

#### **Get All Consents**
```bash
curl -X GET http://localhost:8000/consent/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

---

### **8. Emergency Access Endpoints**

#### **Trigger Emergency Access**
```bash
curl -X POST http://localhost:8000/emergency/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "requested_by": "emt-user-uuid",
    "reason": "Road accident - critical condition",
    "location": "City Hospital ER"
  }'
```

#### **Get Emergency Access Data**
```bash
curl -X GET http://localhost:8000/emergency/access/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

---

### **9. Health Profile Endpoints**

#### **Get Health Profile**
```bash
curl -X GET http://localhost:8000/health-profile/{patient_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### **Add Health Condition**
```bash
curl -X POST http://localhost:8000/health-profile/conditions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "condition": "Diabetes Type 2",
    "severity": "moderate"
  }'
```

#### **Add Allergy**
```bash
curl -X POST http://localhost:8000/health-profile/allergies \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient-uuid",
    "allergen": "Penicillin",
    "severity": "high",
    "reaction": "Anaphylaxis"
  }'
```

---

## 🧪 Automated Testing Script

### **Run All Tests**
```bash
chmod +x test_all_endpoints.sh
./test_all_endpoints.sh
```

### **Custom Test Script**
Create `my_test.sh`:
```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# Login
TOKEN=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr_smith","password":"Doctor@123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Test endpoints
echo "Testing patients..."
curl -s -X GET $BASE_URL/patients/ \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo "Testing health check..."
curl -s $BASE_URL/health | python3 -m json.tool

echo "Done!"
```

---

## 📊 Testing Checklist

### **Core Functionality:**
- [ ] Health check returns 200
- [ ] Login works for all roles
- [ ] JWT token generation successful
- [ ] Patient registration works
- [ ] Biometric verification functional

### **NEW Features:**
- [ ] Clinical notes created successfully
- [ ] Notes encrypted and decrypted correctly
- [ ] Role-based access enforced (doctor/patient/admin)
- [ ] PDF upload works (admin only)
- [ ] Blood values extracted from PDF
- [ ] Original PDF downloadable

### **Security:**
- [ ] Unauthorized access returns 401
- [ ] Wrong credentials rejected
- [ ] Admin-only endpoints protected
- [ ] Notes properly encrypted
- [ ] Biometric data hashed (not stored raw)

### **Error Handling:**
- [ ] Invalid patient ID returns 404
- [ ] Missing required fields returns 422
- [ ] Large file upload rejected
- [ ] Invalid file type rejected

---

## 🎯 Expected Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | No/invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Backend error |

---

## 🐛 Common Issues & Solutions

### **Issue: 401 Unauthorized**
**Solution:** Make sure you're including the Bearer token:
```bash
-H "Authorization: Bearer $TOKEN"
```

### **Issue: 404 Not Found**
**Solution:** Check that the resource ID exists and the endpoint path is correct.

### **Issue: 422 Validation Error**
**Solution:** Check that all required fields are included with correct data types.

### **Issue: PDF Upload Fails**
**Solution:** 
- Ensure you're logged in as admin
- Check file size is under 10MB
- Use `-F` for multipart form data, not `-d`

---

## 📞 Interactive Testing

**Best Way:** Use Swagger UI at `http://localhost:8000/docs`

1. Click "Authorize" button
2. Login to get token
3. Paste token in authorization popup
4. Try endpoints interactively
5. See request/response schemas
6. Download response as JSON

---

**Testing Status:** ✅ All 36 Endpoints Available  
**Documentation:** ✅ Complete  
**Ready to Test:** ✅ YES
