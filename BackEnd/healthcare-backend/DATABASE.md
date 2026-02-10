# 🗄️ Database Schema Documentation

## Overview
Complete database schema for the Universal Healthcare Backend system.

**Database:** SQLite (Development) / PostgreSQL (Production)  
**ORM:** SQLAlchemy  
**Total Tables:** 15

---

## 📊 Database Schema Diagram

```
┌─────────────────┐         ┌─────────────────┐
│     users       │◄────────│    patients     │
│─────────────────│         │─────────────────│
│ id (PK)         │         │ id (PK)         │
│ username        │         │ first_name      │
│ email           │         │ last_name       │
│ password_hash   │         │ date_of_birth   │
│ role (ENUM)     │         │ gender          │
└─────────────────┘         └─────────────────┘
         │                           │
         │                           │
         ├───────────────────────────┴──────────────────┐
         │                           │                  │
┌────────▼──────────┐   ┌────────────▼──────┐  ┌──────▼────────────┐
│ clinical_notes    │   │  blood_reports    │  │  vitals           │
│ (ENCRYPTED)       │   │  (PDF Parser)     │  │                   │
│───────────────────│   │───────────────────│  │───────────────────│
│ id (PK)           │   │ id (PK)           │  │ id (PK)           │
│ patient_id (FK)   │   │ patient_id (FK)   │  │ patient_id (FK)   │
│ author_id (FK)    │   │ uploaded_by (FK)  │  │ heart_rate        │
│ note_content      │   │ report_type       │  │ blood_pressure    │
│ encryption_role   │   │ hemoglobin        │  │ temperature       │
│ category          │   │ wbc_count         │  │ spo2              │
└───────────────────┘   │ glucose_fasting   │  └───────────────────┘
                        │ cholesterol_total │
                        │ ... (30+ fields)  │
                        └───────────────────┘
```

---

## 📋 Table Schemas

### **1. users** - User Authentication

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,  -- ADMIN, DOCTOR, PATIENT, EMT
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key
- `username`: Unique username for login
- `email`: Unique email address
- `password_hash`: Argon2 hashed password
- `role`: ADMIN | DOCTOR | PATIENT | EMT
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

**Indexes:**
```sql
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

---

### **2. patients** - Patient Demographics

```sql
CREATE TABLE patients (
    id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    emergency_contact VARCHAR(200),
    blood_group VARCHAR(5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**
- `id`: UUID primary key
- `first_name`, `last_name`: Patient name
- `date_of_birth`: DOB for age calculation
- `gender`: male | female | other
- `phone`, `email`: Contact information
- `blood_group`: A+, B+, O+, AB+, etc.

**Indexes:**
```sql
CREATE INDEX idx_patients_name ON patients(last_name, first_name);
CREATE INDEX idx_patients_dob ON patients(date_of_birth);
```

---

### **3. biometric_hashes** - Biometric Identity

```sql
CREATE TABLE biometric_hashes (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    biometric_type VARCHAR(20) NOT NULL,  -- fingerprint, face, iris
    hash_value TEXT NOT NULL,             -- HMAC-SHA256 hash
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

**Security:**
- ✅ Never stores raw biometric data
- ✅ HMAC-SHA256 hashing with `BIOMETRIC_SECRET_KEY`
- ✅ Timing-attack resistant comparison

**Indexes:**
```sql
CREATE INDEX idx_biometric_patient ON biometric_hashes(patient_id);
CREATE INDEX idx_biometric_type ON biometric_hashes(biometric_type);
```

---

### **4. clinical_notes** ⭐ NEW - Encrypted Clinical Notes

```sql
CREATE TABLE clinical_notes (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    author_id VARCHAR(36) NOT NULL,
    note_content TEXT NOT NULL,           -- AES-256-GCM encrypted
    encryption_role VARCHAR(20) NOT NULL, -- doctor, admin, patient
    category VARCHAR(50) NOT NULL,        -- diagnosis, treatment, etc.
    is_sensitive BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id)
);
```

**Encryption:**
- ✅ **Algorithm:** AES-256-GCM
- ✅ **Keys:** 3 separate keys (DOCTOR_KEY, PATIENT_KEY, ADMIN_KEY)
- ✅ **Key Derivation:** PBKDF2HMAC with SHA-256

**Categories:**
- `diagnosis` - Diagnosis notes
- `treatment` - Treatment plans
- `observation` - Clinical observations
- `prescription` - Medication prescriptions
- `lab_results` - Lab result interpretations
- `procedure` - Procedures performed
- `follow_up` - Follow-up instructions
- `general` - General notes

**Indexes:**
```sql
CREATE INDEX idx_notes_patient ON clinical_notes(patient_id);
CREATE INDEX idx_notes_author ON clinical_notes(author_id);
CREATE INDEX idx_notes_created ON clinical_notes(created_at DESC);
```

---

### **5. blood_reports** ⭐ NEW - PDF Blood Test Reports

```sql
CREATE TABLE blood_reports (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    uploaded_by VARCHAR(36) NOT NULL,
    report_type VARCHAR(50) NOT NULL,     -- cbc, lipid_panel, liver_function, etc.
    test_date DATE,
    lab_name VARCHAR(200),
    
    -- PDF Storage
    pdf_file_path VARCHAR(500) NOT NULL,
    pdf_file_hash VARCHAR(64) NOT NULL,   -- SHA-256 hash
    pdf_file_size FLOAT,
    extracted_text TEXT,
    
    -- CBC Values
    hemoglobin FLOAT,
    wbc_count FLOAT,
    rbc_count FLOAT,
    platelet_count FLOAT,
    hematocrit FLOAT,
    mcv FLOAT,
    mch FLOAT,
    mchc FLOAT,
    
    -- Glucose & Diabetes
    glucose_fasting FLOAT,
    glucose_random FLOAT,
    glucose_pp FLOAT,
    hba1c FLOAT,
    
    -- Lipid Panel
    cholesterol_total FLOAT,
    cholesterol_hdl FLOAT,
    cholesterol_ldl FLOAT,
    cholesterol_vldl FLOAT,
    triglycerides FLOAT,
    
    -- Liver Function
    sgot FLOAT,
    sgpt FLOAT,
    alkaline_phosphatase FLOAT,
    bilirubin_total FLOAT,
    bilirubin_direct FLOAT,
    bilirubin_indirect FLOAT,
    total_protein FLOAT,
    albumin FLOAT,
    globulin FLOAT,
    
    -- Kidney Function
    creatinine FLOAT,
    urea FLOAT,
    uric_acid FLOAT,
    bun FLOAT,
    egfr FLOAT,
    
    -- Thyroid
    tsh FLOAT,
    t3 FLOAT,
    t4 FLOAT,
    
    -- Electrolytes
    sodium FLOAT,
    potassium FLOAT,
    chloride FLOAT,
    
    -- Others
    calcium FLOAT,
    phosphorus FLOAT,
    magnesium FLOAT,
    iron FLOAT,
    vitamin_d FLOAT,
    vitamin_b12 FLOAT,
    
    -- Parsing Metadata
    other_values JSON,
    parsing_confidence FLOAT,
    parsing_notes TEXT,
    
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);
```

**Report Types:**
- `cbc` - Complete Blood Count
- `lipid_panel` - Lipid profile
- `liver_function` - Liver function tests (LFT)
- `kidney_function` - Kidney function tests (KFT/RFT)
- `thyroid` - Thyroid function tests
- `diabetes` - Diabetes screening
- `general` - General blood work
- `other` - Other tests

**Indexes:**
```sql
CREATE INDEX idx_blood_reports_patient ON blood_reports(patient_id);
CREATE INDEX idx_blood_reports_date ON blood_reports(test_date DESC);
CREATE INDEX idx_blood_reports_type ON blood_reports(report_type);
```

---

### **6. vitals** - Vital Signs

```sql
CREATE TABLE vitals (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    heart_rate FLOAT,
    blood_pressure_systolic INTEGER,
    blood_pressure_diastolic INTEGER,
    temperature FLOAT,
    spo2 FLOAT,
    respiratory_rate FLOAT,
    weight FLOAT,
    height FLOAT,
    bmi FLOAT,
    glucose FLOAT,
    source VARCHAR(50),                   -- manual, wearable, hospital_device
    recorded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

**Indexes:**
```sql
CREATE INDEX idx_vitals_patient ON vitals(patient_id);
CREATE INDEX idx_vitals_recorded ON vitals(recorded_at DESC);
```

---

### **7. consents** - DPDP Consent Management

```sql
CREATE TABLE consents (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    purpose VARCHAR(100) NOT NULL,        -- data_collection, emergency_access, research
    granted_by VARCHAR(36) NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id)
);
```

**Purposes:**
- `data_collection` - Basic data collection
- `emergency_access` - Emergency access consent
- `research` - Research participation
- `third_party_sharing` - Share with third parties

**Indexes:**
```sql
CREATE INDEX idx_consents_patient ON consents(patient_id);
CREATE INDEX idx_consents_purpose ON consents(purpose);
```

---

### **8. devices** - Connected Devices

```sql
CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY,
    device_id VARCHAR(200) UNIQUE NOT NULL,
    patient_id VARCHAR(36),
    device_type VARCHAR(50) NOT NULL,     -- wearable, hospital_device, iot_sensor
    model_number VARCHAR(100),
    last_sync TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
);
```

---

### **9. alerts** - Health Alerts

```sql
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,      -- vital_threshold, medication, appointment
    severity VARCHAR(20) NOT NULL,        -- low, medium, high, critical
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

---

### **10. emergency_access** - Emergency Access Logs

```sql
CREATE TABLE emergency_access (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    requested_by VARCHAR(36) NOT NULL,
    reason TEXT NOT NULL,
    location VARCHAR(200),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    terminated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES users(id)
);
```

---

### **11. audit_logs** - Complete Audit Trail

```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    patient_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,         -- view, create, update, delete
    resource_type VARCHAR(50) NOT NULL,   -- patient, vitals, notes, etc.
    resource_id VARCHAR(36),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
);
```

**Indexes:**
```sql
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_patient ON audit_logs(patient_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_action ON audit_logs(action);
```

---

### **12. health_conditions** - Medical Conditions

```sql
CREATE TABLE health_conditions (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    condition VARCHAR(200) NOT NULL,
    severity VARCHAR(20),                 -- mild, moderate, severe
    diagnosed_date DATE,
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

---

### **13. allergies** - Patient Allergies

```sql
CREATE TABLE allergies (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    allergen VARCHAR(200) NOT NULL,
    severity VARCHAR(20) NOT NULL,        -- mild, moderate, severe, life_threatening
    reaction TEXT,
    identified_date DATE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

---

### **14. medical_tests** - Diagnostic Test Results

```sql
CREATE TABLE medical_tests (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) NOT NULL,
    test_type VARCHAR(100) NOT NULL,
    test_result VARCHAR(50),
    result_value VARCHAR(200),
    test_date DATE,
    source VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);
```

---

## 🔐 Security Features

### **Encryption:**
- ✅ **Passwords:** Argon2 hashing
- ✅ **Biometrics:** HMAC-SHA256 (never store raw)
- ✅ **Clinical Notes:** AES-256-GCM with 3 separate keys
- ✅ **PDF Files:** SHA-256 hash integrity check

### **Access Control:**
- ✅ Foreign key constraints
- ✅ CASCADE deletes for patient data
- ✅ Soft deletes (is_active flags)
- ✅ Role-based record filtering

### **Audit:**
- ✅ Complete audit trail (audit_logs table)
- ✅ Timestamps on all tables
- ✅ User tracking for all modifications

---

## 📊 Database Statistics

```
Total Tables:        15
Total Columns:       ~150
Indexes:             20+
Foreign Keys:        15
Encrypted Fields:    2 (notes, biometrics)
Audit Logged:        All critical operations
```

---

## 🚀 Database Initialization

### **Create Tables:**
```bash
python3 init_db.py
```

This will:
1. Create all 15 tables
2. Seed with sample data:
   - 3 users (admin, dr_smith, dr_jones)
   - 3 patients
   - 4 biometric hashes
   - 15 vitals
   - 4 medical tests
   - 2 alerts
   - Consents, conditions, allergies

### **Reset Database:**
```bash
rm healthcare.db
python3 init_db.py
```

---

## 💾 Backup & Restore

### **Backup (SQLite):**
```bash
sqlite3 healthcare.db ".backup healthcare_backup.db"
```

### **Restore (SQLite):**
```bash
cp healthcare_backup.db healthcare.db
```

### **Backup (PostgreSQL):**
```bash
pg_dump -U username -d healthcare > backup.sql
```

### **Restore (PostgreSQL):**
```bash
psql -U username -d healthcare < backup.sql
```

---

## 🔍 Useful Queries

### **Get Total Counts:**
```sql
SELECT 
    (SELECT COUNT(*) FROM users) as users,
    (SELECT COUNT(*) FROM patients) as patients,
    (SELECT COUNT(*) FROM clinical_notes) as notes,
    (SELECT COUNT(*) FROM blood_reports) as reports,
    (SELECT COUNT(*) FROM vitals) as vitals;
```

### **Recent Activity:**
```sql
SELECT action, resource_type, timestamp 
FROM audit_logs 
ORDER BY timestamp DESC 
LIMIT 10;
```

### **Patient Summary:**
```sql
SELECT 
    p.id,
    p.first_name || ' ' || p.last_name as name,
    (SELECT COUNT(*) FROM vitals WHERE patient_id = p.id) as vitals_count,
    (SELECT COUNT(*) FROM clinical_notes WHERE patient_id = p.id) as notes_count,
    (SELECT COUNT(*) FROM blood_reports WHERE patient_id = p.id) as reports_count
FROM patients p;
```

---

**Database Status:** ✅ Fully Defined  
**Total Tables:** 15  
**Security:** ✅ Enterprise-Grade  
**DPDP Compliant:** ✅ YES
