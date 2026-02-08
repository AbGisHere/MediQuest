# Quick Reference Guide

Fast reference for common operations in the Universal Healthcare Backend.

## 🚀 Quick Start

```bash
# Setup
./setup.sh

# Create database
createdb healthcare_db

# Start server
uvicorn main:app --reload
```

Access at: http://localhost:8000/docs

---

## 🔐 Authentication Flow

```python
# 1. Register
POST /auth/register
{
  "username": "dr_smith",
  "email": "smith@hospital.com",
  "password": "SecurePass123!",
  "role": "doctor"
}
# Response: { access_token, refresh_token, user_id, role }

# 2. Login
POST /auth/login
{
  "username": "dr_smith",
  "password": "SecurePass123!"
}

# 3. Use token in headers
Authorization: Bearer <access_token>

# 4. Refresh when expired
POST /auth/refresh
{
  "refresh_token": "<refresh_token>"
}
```

---

## 👤 Patient Management

```python
# Register patient
POST /patients/register
Headers: Authorization: Bearer <token>
{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "country": "India",
  "fingerprint_data": "base64_fingerprint"
}

# Verify fingerprint
POST /patients/verify-biometric
{
  "fingerprint_data": "base64_fingerprint"
}
# Returns: patient_id

# Get patient
GET /patients/{patient_id}
```

---

## 📊 Vitals Management

```python
# Upload single vital
POST /vitals/
{
  "patient_id": "uuid",
  "vital_type": "glucose",
  "value": 120,
  "unit": "mg/dL",
  "source": "device",
  "recorded_at": "2026-02-08T10:00:00Z"
}

# Batch upload (offline sync)
POST /vitals/batch
{
  "batch_id": "batch_001",
  "vitals": [
    { /* vital 1 */ },
    { /* vital 2 */ }
  ]
}

# Get vitals
GET /vitals/{patient_id}?vital_type=glucose&limit=100
```

---

## 🔒 Consent Management

```python
# Grant consent
POST /consent/grant
{
  "patient_id": "uuid",
  "purpose": "treatment",  # treatment, emergency, research
  "granted_to_id": "doctor_uuid"  # optional
}

# Check consent
GET /consent/{patient_id}/check/treatment

# Revoke consent
POST /consent/revoke
{
  "patient_id": "uuid",
  "purpose": "treatment"
}
```

---

## 🚨 Emergency Access

```python
# Trigger emergency
POST /emergency/trigger
{
  "patient_id": "uuid",
  "trigger_reason": "Patient unconscious",
  "trigger_keyword": "crash"
}
# Returns: emergency_access_id, expires_at

# Access data (bypasses consent)
GET /emergency/access/{patient_id}?emergency_access_id=uuid

# Terminate early
POST /emergency/terminate/{emergency_access_id}
{
  "termination_reason": "Emergency resolved"
}
```

---

## 🏥 Health Profile

```python
# Get unified profile (DigiLocker equivalent)
GET /health-profile/{patient_id}
# Returns:
# - Demographics
# - Chronic conditions
# - Allergies
# - Recent vitals
# - Recent alerts

# Add condition
POST /health-profile/conditions
{
  "patient_id": "uuid",
  "condition_name": "Type 2 Diabetes",
  "severity": "moderate"
}

# Add allergy
POST /health-profile/allergies
{
  "patient_id": "uuid",
  "allergen": "Penicillin",
  "severity": "severe"
}
```

---

## ⚠️ Alert Thresholds

```python
# Automatic alerts generated on these values:

GLUCOSE:
  > 300 mg/dL    → CRITICAL HIGH
  > 180 mg/dL    → HIGH
  < 70 mg/dL     → LOW
  < 54 mg/dL     → CRITICAL LOW

HEART_RATE:
  > 120 bpm      → HIGH
  < 50 bpm       → LOW

SPO2:
  < 90%          → CRITICAL LOW
  < 95%          → LOW

BLOOD_PRESSURE (systolic):
  > 180 mmHg     → CRITICAL HIGH
  > 140 mmHg     → HIGH
  < 90 mmHg      → LOW

TEMPERATURE:
  > 39.4°C       → HIGH FEVER
  > 38.0°C       → FEVER
  < 35.0°C       → HYPOTHERMIA
```

---

## 🔍 Vital Types

```python
# Supported vital types:
- heart_rate (bpm)
- bp_systolic (mmHg)
- bp_diastolic (mmHg)
- spo2 (%)
- temperature (°C)
- glucose (mg/dL)
- weight (kg)
- height (cm)
- bmi
- respiratory_rate (breaths/min)
- ecg
- steps
- sleep_hours (hours)
- calories
```

---

## 🎭 User Roles

```python
ADMIN:
  ✓ All permissions
  ✓ Delete patients
  ✓ View all audit logs
  ✓ Manage users

DOCTOR:
  ✓ Register patients
  ✓ Upload/read medical data (with consent)
  ✓ Grant consent
  ✓ Trigger emergency access
  ✗ Delete patients (admin only)

PATIENT:
  ✓ Read own data
  ✓ Grant/revoke consent
  ✗ Access other patients
  ✗ Upload vitals
```

---

## 📡 Common HTTP Status Codes

```python
200 OK              - Success
201 Created         - Resource created
204 No Content      - Deleted successfully
400 Bad Request     - Invalid data
401 Unauthorized    - Invalid/missing token
403 Forbidden       - No permission/consent
404 Not Found       - Resource doesn't exist
429 Too Many Req    - Rate limit exceeded
500 Server Error    - Internal error
```

---

## 🛠️ Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run server (dev)
uvicorn main:app --reload

# Run server (production)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Create database
createdb healthcare_db

# Database shell
psql healthcare_db

# Generate secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check logs
sudo journalctl -u healthcare-backend -f
```

---

## 🗄️ Database Commands

```sql
-- Connect
psql healthcare_db

-- View tables
\dt

-- Count records
SELECT COUNT(*) FROM patients;
SELECT COUNT(*) FROM vitals;
SELECT COUNT(*) FROM alerts;

-- Recent vitals
SELECT * FROM vitals 
ORDER BY recorded_at DESC 
LIMIT 10;

-- Active alerts
SELECT * FROM alerts 
WHERE resolved = false 
ORDER BY created_at DESC;

-- Audit trail
SELECT * FROM audit_logs 
ORDER BY created_at DESC 
LIMIT 20;

-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;
SELECT create_hypertable('vitals', 'recorded_at');
```

---

## 🔑 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=<32+ char random string>
ENCRYPTION_KEY=<32+ char random string>

# Optional (with defaults)
ENVIRONMENT=development
DEBUG=True
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
EMERGENCY_ACCESS_DURATION_HOURS=2
CORS_ORIGINS=http://localhost:3000
```

---

## 📝 Common Queries

```python
# Get all patients
GET /patients/?skip=0&limit=100

# Get patient vitals by type
GET /vitals/{patient_id}?vital_type=glucose&limit=50

# Get patient consents
GET /consent/{patient_id}

# Check specific consent
GET /consent/{patient_id}/check/treatment

# Health check
GET /health
```

---

## 🎯 Testing Shortcuts

```bash
# Using curl with variables
export TOKEN="your_access_token"
export PATIENT_ID="patient_uuid"
export BASE="http://localhost:8000"

# Quick tests
curl $BASE/health
curl -H "Authorization: Bearer $TOKEN" $BASE/patients/$PATIENT_ID
curl -H "Authorization: Bearer $TOKEN" $BASE/vitals/$PATIENT_ID
curl -H "Authorization: Bearer $TOKEN" $BASE/health-profile/$PATIENT_ID
```

---

## 🔐 Security Best Practices

```python
✓ Always use HTTPS in production
✓ Rotate SECRET_KEY regularly
✓ Use strong passwords (min 8 chars, mixed case, numbers)
✓ Enable rate limiting
✓ Monitor audit logs
✓ Backup database daily
✓ Keep dependencies updated
✓ Use environment variables for secrets
✓ Enable firewall
✓ Use SSL for database connections
```

---

## 📞 Quick Troubleshooting

```python
Problem: "Could not validate credentials"
→ Check if token is expired (refresh it)
→ Verify Authorization header format: "Bearer <token>"

Problem: "No consent granted"
→ Grant consent via POST /consent/grant
→ Or use emergency access

Problem: "User account is inactive"
→ Check is_active flag in database
→ Admin can reactivate

Problem: "Account locked due to failed attempts"
→ Wait 15 minutes
→ Or admin resets failed_login_attempts to 0

Problem: Database connection failed
→ Check DATABASE_URL in .env
→ Verify PostgreSQL is running
→ Check credentials
```

---

## 📚 Documentation Links

- **Setup**: See README.md
- **API Testing**: See API_TESTING_GUIDE.md
- **Features**: See FEATURES.md
- **Deployment**: See DEPLOYMENT.md
- **Interactive Docs**: http://localhost:8000/docs
- **Postman**: Import Healthcare_API.postman_collection.json

---

## 💡 Pro Tips

```python
# 1. Use batch upload for offline scenarios
#    Collect vitals offline, upload in single batch

# 2. Check consent before operations
#    GET /consent/{id}/check/{purpose} returns boolean

# 3. Emergency access auto-expires
#    Default: 2 hours, configurable

# 4. Vitals auto-trigger alerts
#    No manual alert creation needed

# 5. Audit logs are immutable
#    Never deleted except by retention policy

# 6. Biometric is one-way
#    Can verify but never retrieve original

# 7. Soft delete preserves history
#    is_active flag instead of hard delete

# 8. All timestamps are UTC
#    Convert to local timezone on frontend
```

---

**🎉 Ready to build secure, offline-first healthcare systems!**
