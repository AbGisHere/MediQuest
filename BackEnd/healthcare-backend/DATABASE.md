# Database Schema & Test Data

## 📊 Database Structure

The healthcare backend uses **SQLite** (or PostgreSQL in production) with the following **11 tables**:

### Core Tables

1. **users** - Authentication and user management
2. **patients** - Patient demographics and global UID
3. **biometric_hashes** - SHA-256 fingerprint hashes
4. **consents** - DPDP-compliant consent records
5. **vitals** - Time-series medical vital signs
6. **alerts** - Auto-generated health alerts 
7. **devices** - Medical device registry
8. **emergency_access** - Emergency access logs
9. **audit_logs** - Immutable audit trail
10. **health_conditions** - Chronic health conditions
11. **allergies** - Patient allergies

---

## 🎯 Test Data Provided

### 👥 Users (3 total)

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| `admin` | `Admin@123` | ADMIN | Full system access |
| `dr_smith` | `Doctor@123` | DOCTOR | Primary care doctor |
| `dr_jones` | `Doctor@123` | DOCTOR | Specialist |

**Login Example:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "password": "Doctor@123"
  }'
```

---

### 🏥 Patients (3 total)

#### Patient 1: John Doe
- **Age**: 41 years (DOB: 1985-05-15)
- **Gender**: Male
- **Blood Group**: A+
- **Country**: USA
- **Email**: john.doe@email.com
- **Phone**: +1234567890
- **Emergency Contact**: Jane Doe (Spouse) - +1234567891
- **Registered By**: dr_smith
- **Status**: Healthy
- **Vitals**: 5 heart rate readings (72-76 bpm) - all normal
- ** Allergies**: Penicillin (moderate severity)
- **Biometric**: Fingerprint hash registered

#### Patient 2: Sarah Johnson
- **Age**: 36 years (DOB: 1990-08-22)
- **Gender**: Female
- **Blood Group**: O+
- **Country**: USA
- **Email**: sarah.johnson@email.com
- **Phone**: +1234567892
- **Emergency Contact**: Mike Johnson (Father) - +1234567893
- **Registered By**: dr_smith
- **Status**: Low oxygen episode
- **Vitals**: 5 SpO2 readings (88%-98%) - **1 critical low at 88%**
- **Alerts**: 1 critical low oxygen alert
- **Biometric**: Fingerprint hash registered

#### Patient 3: Michael Williams
- **Age**: 51 years (DOB: 1975-03-10)
- **Gender**: Male
- **Blood Group**: B+
- **Country**: India
- **Email**: michael.williams@email.com
- **Phone**: +1234567894
- **Emergency Contact**: Lisa Williams (Spouse) - +1234567895
- **Registered By**: dr_jones
- **Status**: Diabetic with critical glucose episodes
- **Health Conditions**:
  - Type 2 Diabetes (diagnosed 2020-01-15, moderate severity)
  - Hypertension (diagnosed 2019-06-20, mild severity)
- **Vitals**: 5 glucose readings (95-320 mg/dL) - **2 critical highs**
- **Allergies**: Peanuts (severe - anaphylaxis risk)
- **Alerts**: 1 critical high glucose alert
- **Biometric**: Fingerprint hash registered

---

### 📜 Consents (3 total)

All patients have granted **TREATMENT** consent:

| Patient | Granted To | Purpose | Status |
|---------|------------|---------|--------|
| John Doe | dr_smith | Treatment | ✅ Active |
| Sarah Johnson | dr_smith | Treatment | ✅ Active |
| Michael Williams | dr_jones | Treatment | ✅ Active |

---

### 📊 Vitals (15 total)

#### John Doe - Heart Rate (5 readings)
- All readings: 72-76 bpm (normal range)
- Source: Device
- Recorded over last 5 days

#### Sarah Johnson - SpO2 (5 readings)
- Values: 98%, 97%, 96%, **88%**, 95%
- **Critical**: 88% SpO2 (below 90% threshold)
- Source: Wearable device
- Recorded over last 5 days

#### Michael Williams - Glucose (5 readings)
- Values: 95, 180, **320**, 150, **280** mg/dL
- **Critical**: 320 mg/dL (above 300 threshold)
- **High**: 280 mg/dL, 180 mg/dL (above 180 threshold)
- Source: Glucose monitor device
- Recorded over last 5 days

---

### 🚨 Alerts (2 total)

| Patient | Alert Type | Severity | Value | Threshold |
|---------|-----------|----------|-------|-----------|
| Sarah Johnson | Low Oxygen | CRITICAL | 88% SpO2 | < 90% |
| Michael Williams | High Glucose | CRITICAL | 320 mg/dL | > 300 mg/dL |

---

### 🩺 Health Conditions (2 total)

| Patient | Condition | Severity | Diagnosed | Notes |
|---------|-----------|----------|-----------|-------|
| Michael Williams | Type 2 Diabetes | Moderate | 2020-01-15 | On metformin 500mg twice daily |
| Michael Williams | Hypertension | Mild | 2019-06-20 | Stage 1, monitoring |

---

### ⚠️ Allergies (2 total)

| Patient | Allergen | Reaction | Severity | Diagnosed |
|---------|----------|----------|----------|-----------|
| John Doe | Penicillin | Rash and itching | Moderate | 2015-03-01 |
| Michael Williams | Peanuts | Anaphylaxis | **SEVERE** | 2018-07-10 |

---

### 🔐 Biometric Hashes (3 total)

All 3 patients have SHA-256 fingerprint hashes registered:
- Each hash is unique and globally indexed
- Can be used for biometric verification via `/patients/verify-biometric`
- No raw biometric data is stored

---

## 📝 Database Schema Details

### 1. Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- admin, doctor, patient
    is_active BOOLEAN DEFAULT TRUE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Patients Table
```sql
CREATE TABLE patients (
    id VARCHAR(36) PRIMARY KEY,  -- Global Patient UID
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    email VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    postal_code VARCHAR(20),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relationship VARCHAR(50),
    registered_by VARCHAR(36) REFERENCES users(id),
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Biometric Hashes Table
```sql
CREATE TABLE biometric_hashes (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) UNIQUE REFERENCES patients(id),
    fingerprint_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA-256
    hash_algorithm VARCHAR(20) DEFAULT 'SHA256',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_biometric_fingerprint ON biometric_hashes(fingerprint_hash);
```

### 4. Consents Table
```sql
CREATE TABLE consents (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    purpose VARCHAR(50) NOT NULL,  -- treatment, emergency, research
    granted BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP,
    granted_by VARCHAR(36) REFERENCES users(id),
    granted_to VARCHAR(36) REFERENCES users(id),
    revoked_at TIMESTAMP,
    revoked_by VARCHAR(36) REFERENCES users(id),
    consent_text TEXT,
    expiry_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_consent_patient ON consents(patient_id);
```

### 5. Vitals Table
```sql
CREATE TABLE vitals (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    vital_type VARCHAR(50) NOT NULL,  -- glucose, heart_rate, bp, spo2, etc.
    value FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    source VARCHAR(50),  -- device, doctor, wearable, manual
    source_id VARCHAR(36),
    recorded_at TIMESTAMP NOT NULL,
    batch_id VARCHAR(36),
    notes TEXT,
    checksum VARCHAR(64),
    uploaded_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_vital_patient_time ON vitals(patient_id, recorded_at DESC);
CREATE INDEX idx_vital_type ON vitals(vital_type);
```

### 6. Alerts Table
```sql
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    vital_id VARCHAR(36) REFERENCES vitals(id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,  -- LOW, MEDIUM, HIGH, CRITICAL
    message TEXT NOT NULL,
    trigger_value FLOAT,
    threshold_value FLOAT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(36) REFERENCES users(id),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_alert_patient ON alerts(patient_id);
CREATE INDEX idx_alert_severity ON alerts(severity);
```

### 7. Health Conditions Table
```sql
CREATE TABLE health_conditions (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    condition_name VARCHAR(200) NOT NULL,
    diagnosed_date TIMESTAMP,
    diagnosed_by VARCHAR(36) REFERENCES users(id),
    severity VARCHAR(20),  -- mild, moderate, severe
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 8. Allergies Table
```sql
CREATE TABLE allergies (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    allergen VARCHAR(200) NOT NULL,
    reaction TEXT,
    severity VARCHAR(20),  -- mild, moderate, severe
    diagnosed_date TIMESTAMP,
    diagnosed_by VARCHAR(36) REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 9. Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    action VARCHAR(50) NOT NULL,  -- login_success, patient_viewed, etc.
    actor_id VARCHAR(36) REFERENCES users(id),
    actor_role VARCHAR(20),
    resource_type VARCHAR(50),  -- patient, vital, consent, etc.
    resource_id VARCHAR(36),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    description TEXT,
    audit_metadata JSON,  -- Additional context
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_time ON audit_logs(created_at DESC);
```

### 10. Devices Table
```sql
CREATE TABLE devices (
    id VARCHAR(36) PRIMARY KEY,
    device_name VARCHAR(200) NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(200),
    model_number VARCHAR(100),
    serial_number VARCHAR(100) UNIQUE,
    api_key_hash VARCHAR(255) NOT NULL,
    patient_id VARCHAR(36) REFERENCES patients(id),
    registered_by VARCHAR(36) REFERENCES users(id),
    firmware_version VARCHAR(50),
    software_version VARCHAR(50),
    last_heartbeat TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    device_metadata JSON,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11. Emergency Access Table
```sql
CREATE TABLE emergency_access (
    id VARCHAR(36) PRIMARY KEY,
    patient_id VARCHAR(36) REFERENCES patients(id),
    triggered_by VARCHAR(36) REFERENCES users(id),
    trigger_reason TEXT NOT NULL,
    trigger_keyword VARCHAR(50),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMP,
    hospital_notified BOOLEAN DEFAULT FALSE,
    notification_sent_at TIMESTAMP,
    terminated BOOLEAN DEFAULT FALSE,
    terminated_at TIMESTAMP,
    terminated_by VARCHAR(36) REFERENCES users(id),
    termination_reason TEXT
);
```

---

## 🧪 Testing the Database

### 1. Login as Doctor
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"dr_smith","password":"Doctor@123"}'
```

Save the `access_token` from response.

### 2. Get Patient Profile
```bash
curl http://localhost:8000/health-profile/{patient_id} \
  -H "Authorization: Bearer {access_token}"
```

### 3. View Alerts
Query the database or use the API to see the 2 critical alerts generated.

### 4. Test Biometric Verification
```bash
curl -X POST http://localhost:8000/patients/verify-biometric \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{"fingerprint_data":"fingerprint_{patient_id}"}'
```

---

## 📈 Data Summary

| Category | Count | Status |
|----------|-------|--------|
| Users | 3 | ✅ Ready |
| Patients | 3 | ✅ Ready |
| Biometric Hashes | 3 | ✅ Ready |
| Consents | 3 | ✅ Active |
| Vitals | 15 | ✅ Ready |
| Alerts | 2 | 🚨 Critical |
| Health Conditions | 2 | ✅ Ready |
| Allergies | 2 | ⚠️ Active |

---

## 🔄 Reinitialize Database

To reset and reinitialize:

```bash
rm -f healthcare.db
python init_db.py
# Answer 'y' when prompted
```

---

**The database is fully populated and ready for testing!** 🎉
