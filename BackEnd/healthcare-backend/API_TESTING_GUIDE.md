# API Testing Guide

This guide will walk you through testing the Universal Healthcare Backend API.

## Prerequisites

1. Backend server running at `http://localhost:8000`
2. Database created and configured
3. Postman (optional) or curl

## Quick Test Flow

### 1. Health Check

Verify the server is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0",
  "features": {
    "offline_first": true,
    "biometric_identity": true,
    ...
  }
}
```

### 2. Register a Doctor

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "email": "smith@hospital.com",
    "password": "SecurePass123!",
    "role": "doctor"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "doctor"
}
```

**Important**: Save the `access_token` for subsequent requests!

### 3. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "password": "SecurePass123!"
  }'
```

### 4. Register a Patient

Replace `YOUR_TOKEN` with the access token from step 2:

```bash
curl -X POST http://localhost:8000/patients/register \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "blood_group": "O+",
    "email": "john.doe@email.com",
    "phone": "+1234567890",
    "country": "India",
    "fingerprint_data": "sample_fingerprint_12345"
  }'
```

**Save the patient `id` from the response!**

### 5. Upload Vitals

Replace `YOUR_TOKEN` and `PATIENT_ID`:

```bash
curl -X POST http://localhost:8000/vitals/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PATIENT_ID",
    "vital_type": "glucose",
    "value": 350,
    "unit": "mg/dL",
    "source": "device",
    "recorded_at": "2026-02-08T10:00:00Z"
  }'
```

Note: A glucose value of 350 should trigger a CRITICAL alert!

### 6. Batch Upload (Offline Support)

```bash
curl -X POST http://localhost:8000/vitals/batch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "offline_batch_001",
    "vitals": [
      {
        "patient_id": "PATIENT_ID",
        "vital_type": "heart_rate",
        "value": 75,
        "unit": "bpm",
        "source": "wearable",
        "recorded_at": "2026-02-08T09:00:00Z"
      },
      {
        "patient_id": "PATIENT_ID",
        "vital_type": "spo2",
        "value": 85,
        "unit": "%",
        "source": "wearable",
        "recorded_at": "2026-02-08T09:01:00Z"
      }
    ]
  }'
```

Note: SpO2 of 85% should trigger a CRITICAL low oxygen alert!

### 7. Get Unified Health Profile

```bash
curl -X GET http://localhost:8000/health-profile/PATIENT_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

This returns the complete DigiLocker-style health profile with:
- Patient demographics
- Chronic conditions
- Allergies
- Recent vitals
- Recent alerts

### 8. Verify Biometric

```bash
curl -X POST http://localhost:8000/patients/verify-biometric \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fingerprint_data": "sample_fingerprint_12345"
  }'
```

This returns the patient ID linked to the fingerprint.

### 9. Emergency Access

Trigger emergency access (bypasses consent):

```bash
curl -X POST http://localhost:8000/emergency/trigger \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PATIENT_ID",
    "trigger_reason": "Patient unconscious, immediate care needed",
    "trigger_keyword": "crash"
  }'
```

Save the `emergency_access_id` from response, then access data:

```bash
curl -X GET "http://localhost:8000/emergency/access/PATIENT_ID?emergency_access_id=EMERGENCY_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 10. Grant Consent

```bash
curl -X POST http://localhost:8000/consent/grant \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PATIENT_ID",
    "purpose": "treatment"
  }'
```

### 11. Check Consent

```bash
curl -X GET http://localhost:8000/consent/PATIENT_ID/check/treatment \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Alert Triggers

Test the alert engine with these values:

### Diabetes Alerts
- **Critical High**: Glucose > 300 mg/dL
- **High**: Glucose > 180 mg/dL
- **Low**: Glucose < 70 mg/dL
- **Critical Low**: Glucose < 54 mg/dL

### Heart Rate Alerts
- **High**: Heart rate > 120 bpm
- **Low**: Heart rate < 50 bpm

### Oxygen Saturation
- **Critical Low**: SpO2 < 90%
- **Low**: SpO2 < 95%

### Blood Pressure
- **Critical High**: Systolic > 180 mmHg
- **High**: Systolic > 140 mmHg
- **Low**: Systolic < 90 mmHg

### Temperature
- **High Fever**: > 39.4°C (103°F)
- **Fever**: > 38.0°C (100.4°F)
- **Hypothermia**: < 35.0°C (95°F)

## Full Test Sequence

```bash
#!/bin/bash

# 1. Register doctor
RESPONSE=$(curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"dr_test","email":"test@example.com","password":"Test123!","role":"doctor"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

# 2. Register patient
PATIENT=$(curl -s -X POST http://localhost:8000/patients/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"Patient","date_of_birth":"1990-01-01","country":"India","fingerprint_data":"test_fp_123"}')

PATIENT_ID=$(echo $PATIENT | jq -r '.id')
echo "Patient ID: $PATIENT_ID"

# 3. Upload critical glucose
curl -X POST http://localhost:8000/vitals/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"patient_id\":\"$PATIENT_ID\",\"vital_type\":\"glucose\",\"value\":350,\"unit\":\"mg/dL\",\"source\":\"device\",\"recorded_at\":\"2026-02-08T10:00:00Z\"}"

# 4. Get health profile
curl -X GET http://localhost:8000/health-profile/$PATIENT_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Using Postman

1. Import `Healthcare_API.postman_collection.json`
2. Set variables:
   - `baseUrl`: http://localhost:8000
   - `accessToken`: (from login response)
   - `patientId`: (from patient registration)
3. Run requests in order

## Interactive Documentation

Visit http://localhost:8000/docs for interactive API testing via Swagger UI.

## Common Issues

### 403 Forbidden
- Check if consent is granted
- Verify user role has permission
- Check if emergency access is needed

### 401 Unauthorized
- Token expired (refresh it)
- Token not provided
- Invalid token

### 429 Too Many Requests
- Brute force protection triggered
- Wait 15 minutes or check failed login attempts

## Audit Logs

All actions are logged. Admins can query audit logs (feature to be implemented in admin router).

## Security Testing

### Test Brute Force Protection

Try logging in with wrong password 6 times:

```bash
for i in {1..6}; do
  curl -X POST http://localhost:8000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"dr_smith","password":"wrongpass"}'
  echo "Attempt $i"
done
```

Account should be locked after 5 attempts.

### Test Consent Enforcement

1. Register patient
2. DON'T grant consent
3. Try to access patient data
4. Should get 403 Forbidden

### Test Emergency Override

1. Trigger emergency access
2. Access patient data WITHOUT consent
3. Check audit logs - should show emergency access
4. Verify auto-expiry after 2 hours

## Production Checklist

Before going to production:

- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY and ENCRYPTION_KEY
- [ ] Set ENVIRONMENT=production
- [ ] Set DEBUG=False
- [ ] Use PostgreSQL with SSL
- [ ] Enable HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Review rate limits
- [ ] Test emergency procedures
- [ ] Audit compliance
