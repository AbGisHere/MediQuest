"""
Realistic data seeder for healthcare backend.
Generates 100 patients with realistic medical profiles and conditions.
"""
from app.database import Base, engine, SessionLocal
from app.models import *
from app.auth.password import hash_password
from app.services.biometric import hash_fingerprint
from app.services.alerts import AlertEngine
import uuid
from datetime import datetime, timezone, timedelta
import random
import hashlib
import hmac

# Realistic name pools
FIRST_NAMES_MALE = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Christopher", 
                     "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Andrew", "Kenneth", "Joshua", "Kevin",
                     "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob", "Gary"]

FIRST_NAMES_FEMALE = ["Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan", "Jessica", "Sarah", "Karen",
                       "Lisa", "Nancy", "Betty", "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
                       "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
              "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
              "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores"]

BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Mumbai", "Delhi", "Bangalore", "London", "Tokyo"]
COUNTRIES = ["USA", "India", "UK", "Canada", "Australia"]

# Medical data
ALLERGIES_POOL = ["Penicillin", "Peanuts", "Shellfish", "Latex", "Aspirin", "Pollen", "Dust mites", "Pet dander", 
                   "Sulfa drugs", "Iodine", "Egg", "Milk", "Soy", "Wheat"]

VITAL_SOURCES = ["doctor", "device", "wearable"]

def generate_realistic_vitals(patient_id, patient_condition, db):
    """Generate 10-15 vitals for a patient based on their condition."""
    num_vitals = random.randint(10, 15)
    vitals = []
    now = datetime.now(timezone.utc)
    
    for i in range(num_vitals):
        # Spread over last 30 days
        days_ago = random.randint(0, 30)
        recorded_at = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # Choose source with weights
        source = random.choices(VITAL_SOURCES, weights=[40, 40, 20])[0]
        
        # Generate different vitals based on condition
        vital_types_to_generate = []
        
        if patient_condition in ["diabetic", "diabetic_hypertensive"]:
            vital_types_to_generate.append(("glucose", True))  # Always glucose for diabetics
            
        if patient_condition in ["hypertensive", "diabetic_hypertensive"]:
            vital_types_to_generate.append(("bp_systolic", True))
            vital_types_to_generate.append(("bp_diastolic", False))
            
        # Add common vitals
        if random.random() < 0.7:
            vital_types_to_generate.append(("heart_rate", False))
        if random.random() < 0.5:
            vital_types_to_generate.append(("spo2", False))
        if random.random() < 0.3:
            vital_types_to_generate.append(("temperature", False))
        
        # Generate the vitals
        for vital_type, is_primary in vital_types_to_generate[:2]:  # Max 2 vital types per timestamp
            value, unit = generate_vital_value(vital_type, patient_condition)
            
            vital = Vital(
                patient_id=patient_id,
                vital_type=vital_type,
                value=value,
                unit=unit,
                source=source,
                source_id=str(uuid.uuid4()),
                recorded_at=recorded_at,
                uploaded_by=str(uuid.uuid4())
            )
            vitals.append(vital)
            db.add(vital)
    
    return vitals

def generate_vital_value(vital_type, condition):
    """Generate realistic vital values based on patient condition."""
    
    if vital_type == "glucose":
        if condition in ["diabetic", "diabetic_hypertensive"]:
            # Diabetic patients have more variable glucose
            if random.random() < 0.15:  # 15% chance of critical high
                value = random.randint(301, 400)
            elif random.random() < 0.25:  # 25% chance of high
                value = random.randint(181, 300)
            elif random.random() < 0.10:  # 10% chance of low
                value = random.randint(60, 69)
            else:  # 50% normal range for diabetics
                value = random.randint(90, 180)
        else:
            # Healthy: mostly normal
            value = random.randint(70, 120)
        return value, "mg/dL"
    
    elif vital_type == "bp_systolic":
        if condition in ["hypertensive", "diabetic_hypertensive"]:
            # Hypertensive patients
            if random.random() < 0.10:  # 10% critical
                value = random.randint(181, 200)
            elif random.random() < 0.30:  # 30% high
                value = random.randint(141, 180)
            else:  # 60% controlled
                value = random.randint(120, 140)
        else:
            value = random.randint(110, 130)
        return value, "mmHg"
    
    elif vital_type == "bp_diastolic":
        if condition in ["hypertensive", "diabetic_hypertensive"]:
            value = random.randint(75, 95)
        else:
            value = random.randint(70, 85)
        return value, "mmHg"
    
    elif vital_type == "heart_rate":
        if random.random() < 0.05:  # 5% abnormal
            value = random.choice([random.randint(45, 49), random.randint(121, 130)])
        else:
            value = random.randint(60, 100)
        return value, "bpm"
    
    elif vital_type == "spo2":
        if random.random() < 0.05:  # 5% low
            value = random.randint(88, 94)
        else:
            value = random.randint(95, 100)
        return value, "%"
    
    elif vital_type == "temperature":
        if random.random() < 0.05:  # 5% fever
            value = round(random.uniform(38.1, 39.5), 1)
        else:
            value = round(random.uniform(36.5, 37.5), 1)
        return value, "°C"
    
    else:
        return random.randint(70, 120), "unit"

def seed_large_realistic_data():
    """Seed realistic large-scale data."""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("🏥 SEEDING REALISTIC LARGE-SCALE DATA")
        print("=" * 70)
        
        # 1. Create Admins (2)
        print("\n👑 Creating 2 Admins...")
        admins = []
        for i in range(2):
            admin = User(
                id=str(uuid.uuid4()),
                username=f"admin{i+1}",
                email=f"admin{i+1}@healthcare.com",
                password_hash=hash_password("Admin@123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            admins.append(admin)
            db.add(admin)
        db.commit()
        print(f"   ✅ Created {len(admins)} admins")
        
        # 2. Create Doctors (8)
        print("\n👨‍⚕️ Creating 8 Doctors...")
        doctors = []
        doctor_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        for i, name in enumerate(doctor_names):
            doctor = User(
                id=str(uuid.uuid4()),
                username=f"dr_{name.lower()}",
                email=f"{name.lower()}@hospital.com",
                password_hash=hash_password("Doctor@123"),
                role=UserRole.DOCTOR,
                is_active=True
            )
            doctors.append(doctor)
            db.add(doctor)
        db.commit()
        print(f"   ✅ Created {len(doctors)} doctors")
        
        # 3. Create 100 Patient Users
        print("\n👥 Creating 100 Patient Users...")
        patient_users = []
        for i in range(100):
            gender = random.choice(["male", "female"])
            first_name = random.choice(FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE)
            last_name = random.choice(LAST_NAMES)
            
            patient_user = User(
                id=str(uuid.uuid4()),
                username=f"{first_name.lower()}.{last_name.lower()}{i}",
                email=f"{first_name.lower()}.{last_name.lower()}{i}@email.com",
                password_hash=hash_password("Patient@123"),
                role=UserRole.PATIENT,
                is_active=True
            )
            patient_users.append(patient_user)
            db.add(patient_user)
        db.commit()
        print(f"   ✅ Created {len(patient_users)} patient users")
        
        # 4. Determine patient conditions (100 patients)
        print("\n🏥 Generating Patient Conditions Distribution...")
        conditions_distribution = (
            ["healthy"] * 60 +
            ["diabetic"] * 20 +
            ["hypertensive"] * 10 +
            ["diabetic_hypertensive"] * 5 +
            ["asthma"] * 3 +
            ["cardiac"] * 2
        )
        random.shuffle(conditions_distribution)
        
        print("   📊 Distribution:")
        print(f"      60 healthy | 20 diabetic | 10 hypertensive")
        print(f"      5 diabetic+hypertensive | 3 asthma | 2 cardiac")
        
        # 5. Create 100 Patients with demographics
        print("\n🏥 Creating 100 Patients...")
        patients = []
        biometric_hashes = []
        
        for i in range(100):
            condition = conditions_distribution[i]
            gender = random.choice(["male", "female"])
            first_name = random.choice(FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE)
            last_name = random.choice(LAST_NAMES)
            
            # Age distribution: 20-80 years
            age = random.randint(20, 80)
            dob = datetime.now() - timedelta(days=age*365)
            
            # Assign to random doctor
            assigned_doctor = random.choice(doctors)
            
            patient = Patient(
                id=str(uuid.uuid4()),
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob.date(),
                gender=gender,
                blood_group=random.choice(BLOOD_GROUPS),
                email=f"{first_name.lower()}.{last_name.lower()}{i}@email.com",
                phone=f"+1{random.randint(2000000000, 9999999999)}",
                city=random.choice(CITIES),
                country=random.choice(COUNTRIES),
                emergency_contact_name=f"Emergency Contact {i}",
                emergency_contact_phone=f"+1{random.randint(2000000000, 9999999999)}",
                emergency_contact_relationship=random.choice(["Spouse", "Parent", "Sibling", "Child"]),
                registered_by=assigned_doctor.id,
                is_active=True
            )
            patient.condition_type = condition  # Temporary attribute for later use
            patients.append(patient)
            db.add(patient)
            
            # Create biometric hash using HMAC
            secret_key = "healthcare_secret_key_2026"
            fingerprint_data = f"fingerprint_{patient.id}"
            fingerprint_hash = hmac.new(
                secret_key.encode(),
                fingerprint_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            bio_hash = BiometricHash(
                patient_id=patient.id,
                fingerprint_hash=fingerprint_hash,
                hash_algorithm="HMAC_SHA256"
            )
            biometric_hashes.append(bio_hash)
            db.add(bio_hash)
        
        db.commit()
        print(f"   ✅ Created {len(patients)} patients")
        print(f"   ✅ Created {len(biometric_hashes)} biometric hashes")
        
        # 6. Create Consents (100)
        print("\n📜 Creating Consent Records...")
        consents = []
        for patient in patients:
            # Everyone gets treatment consent
            consent = Consent(
                patient_id=patient.id,
                purpose=ConsentPurpose.TREATMENT,
                granted=True,
                granted_by=patient.id,
                granted_to=patient.registered_by
            )
            consents.append(consent)
            db.add(consent)
            
            # 20% get research consent
            if random.random() < 0.20:
                research_consent = Consent(
                    patient_id=patient.id,
                    purpose=ConsentPurpose.RESEARCH,
                    granted=True,
                    granted_by=patient.id,
                    granted_to=patient.registered_by
                )
                consents.append(research_consent)
                db.add(research_consent)
        
        db.commit()
        print(f"   ✅ Created {len(consents)} consent records")
        
        # 7. Create Health Conditions (~160)
        print("\n🩺 Creating Health Conditions...")
        health_conditions = []
        
        for patient in patients:
            condition_type = patient.condition_type
            
            if condition_type == "diabetic":
                hc = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Type 2 Diabetes",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 3650)),
                    diagnosed_by=patient.registered_by,
                    severity=random.choice(["mild", "moderate", "severe"]),
                    notes="Patient on diabetes management",
                    is_active=True
                )
                health_conditions.append(hc)
                db.add(hc)
                
            elif condition_type == "hypertensive":
                hc = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Hypertension",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 3650)),
                    diagnosed_by=patient.registered_by,
                    severity=random.choice(["mild", "moderate"]),
                    notes="Blood pressure monitoring required",
                    is_active=True
                )
                health_conditions.append(hc)
                db.add(hc)
                
            elif condition_type == "diabetic_hypertensive":
                # Diabetes
                hc1 = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Type 2 Diabetes",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(730, 3650)),
                    diagnosed_by=patient.registered_by,
                    severity=random.choice(["moderate", "severe"]),
                    notes="Comorbid with hypertension",
                    is_active=True
                )
                health_conditions.append(hc1)
                db.add(hc1)
                
                # Hypertension
                hc2 = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Hypertension",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 3650)),
                    diagnosed_by=patient.registered_by,
                    severity=random.choice(["moderate", "severe"]),
                    notes="Comorbid with diabetes",
                    is_active=True
                )
                health_conditions.append(hc2)
                db.add(hc2)
                
            elif condition_type == "asthma":
                hc = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Asthma",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 7300)),
                    diagnosed_by=patient.registered_by,
                    severity=random.choice(["mild", "moderate"]),
                    notes="Requires inhaler",
                    is_active=True
                )
                health_conditions.append(hc)
                db.add(hc)
                
            elif condition_type == "cardiac":
                hc = HealthCondition(
                    patient_id=patient.id,
                    condition_name="Coronary Artery Disease",
                    diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 3650)),
                    diagnosed_by=patient.registered_by,
                    severity="moderate",
                    notes="Regular cardiac monitoring",
                    is_active=True
                )
                health_conditions.append(hc)
                db.add(hc)
        
        db.commit()
        print(f"   ✅ Created {len(health_conditions)} health conditions")
        
        # 8. Create Allergies (~90)  
        print("\n⚠️  Creating Allergies...")
        allergies = []
        
        # 90% of patients have 1 allergy
        patients_with_allergies = random.sample(patients, 90)
        
        for patient in patients_with_allergies:
            allergen = random.choice(ALLERGIES_POOL)
            reactions = {
                "Penicillin": "Rash and hives",
                "Peanuts": "Anaphylaxis",
                "Shellfish": "Swelling and difficulty breathing",
                "Latex": "Skin irritation",
                "Aspirin": "Stomach upset and bleeding",
                "Pollen": "Sneezing and itchy eyes",
                "Dust mites": "Runny nose and sneezing",
                "Pet dander": "Itchy eyes and sneezing"
            }
            
            allergy = Allergy(
                patient_id=patient.id,
                allergen=allergen,
                reaction=reactions.get(allergen, "Allergic reaction"),
                severity=random.choice(["mild", "moderate", "severe"]),
                diagnosed_date=datetime.now(timezone.utc) - timedelta(days=random.randint(365, 7300)),
                diagnosed_by=patient.registered_by,
                is_active=True
            )
            allergies.append(allergy)
            db.add(allergy)
        
        db.commit()
        print(f"   ✅ Created {len(allergies)} allergies")
        
        # 9. Generate Vitals (~1,200 total)
        print("\n📊 Generating ~1,200 Vitals...")
        all_vitals = []
        
        for patient in patients:
            vitals = generate_realistic_vitals(patient.id, patient.condition_type, db)
            all_vitals.extend(vitals)
        
        db.commit()
        print(f"   ✅ Created {len(all_vitals)} vital records")
        
        # 10. Generate Alerts (only for abnormal vitals)
        print("\n🚨 Generating Alerts (threshold-based only)...")
        alerts_count = 0
        
        for vital in all_vitals:
            alert = AlertEngine.evaluate_vital(db, vital)
            if alert:
                alerts_count += 1
        
        print(f"   ✅ Generated {alerts_count} alerts")
        
        # 11. Create Devices (15)
        print("\n📱 Creating 15 Medical Devices...")
        devices = []
        device_types_list = [
            ("Glucose Monitor Pro", DeviceType.GLUCOSE_MONITOR),
            ("BP Cuff Digital", DeviceType.BLOOD_PRESSURE_MONITOR),
            ("Pulse Oximeter X1", DeviceType.PULSE_OXIMETER),
            ("SmartWatch Health", DeviceType.SMARTWATCH),
            ("ECG Monitor", DeviceType.ECG_MONITOR),
        ]
        
        for i in range(15):
            device_name, device_type = random.choice(device_types_list)
            device = Device(
                id=str(uuid.uuid4()),
                device_name=f"{device_name} #{i+1}",
                device_type=device_type.value,
                manufacturer=random.choice(["MedTech", "HealthCorp", "VitalSystems"]),
                model_number=f"MODEL-{random.randint(1000, 9999)}",
                serial_number=f"SN{random.randint(100000, 999999)}",
                api_key_hash=hash_password(f"device_key_{i}"),
                patient_id=random.choice(patients).id if random.random() < 0.7 else None,
                registered_by=random.choice(doctors).id,
                firmware_version=f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                is_active=True
            )
            devices.append(device)
            db.add(device)
        
        db.commit()
        print(f"   ✅ Created {len(devices)} devices")
        
        # 12. Create Emergency Access Records (5)
        print("\n🚨 Creating 5 Emergency Access Records...")
        emergency_records = []
        
        for i in range(5):
            emergency = EmergencyAccess(
                patient_id=random.choice(patients).id,
                triggered_by=random.choice(doctors).id,
                trigger_reason=random.choice([
                    "Patient unconscious in ER",
                    "Cardiac arrest - immediate access needed",
                    "Severe trauma - no patient response",
                    "Anaphylactic shock",
                    "Road accident - patient critical"
                ]),
                trigger_keyword=random.choice(["crash", "emergency", "critical"]),
                granted_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
                is_active=random.choice([True, False]),
                access_count=random.randint(0, 5),
                hospital_notified=True
            )
            emergency_records.append(emergency)
            db.add(emergency)
        
        db.commit()
        print(f"   ✅ Created {len(emergency_records)} emergency access records")
        
        # 13. Generate Audit Logs (~3,000)
        print("\n📝 Generating ~3,000 Audit Logs...")
        audit_actions = [
            AuditAction.LOGIN_SUCCESS,
            AuditAction.PATIENT_VIEWED,
            AuditAction.VITAL_UPLOADED,
            AuditAction.CONSENT_GRANTED,
            AuditAction.PATIENT_REGISTERED
        ]
        
        for i in range(3000):
            audit = AuditLog(
                action=random.choice(audit_actions),
                actor_id=random.choice(doctors + admins).id,
                actor_role=random.choice(["doctor", "admin"]),
                resource_type=random.choice(["patient", "vital", "consent"]),
                resource_id=str(uuid.uuid4()),
                description=f"Audit event {i+1}",
                success=random.random() < 0.95,  # 95% success rate
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 90))
            )
            db.add(audit)
            
            if i % 500 == 0:
                db.commit()
        
        db.commit()
        print(f"   ✅ Created ~3,000 audit logs")
        
        # Final Summary
        print("\n" + "=" * 70)
        print("📊 FINAL DATA SUMMARY")
        print("=" * 70)
        print(f"👥 Users: 110 (2 admins, 8 doctors, 100 patients)")
        print(f"🏥 Patients: 100 with realistic demographics")
        print(f"🔐 Biometric Hashes: 100 (HMAC_SHA256)")
        print(f"📜 Consents: {len(consents)} (100 treatment + 20% research)")
        print(f"📊 Vitals: {len(all_vitals)} (10-15 per patient)")
        print(f"🚨 Alerts: {alerts_count} (ONLY threshold-based)")
        print(f"🩺 Health Conditions: {len(health_conditions)}")
        print(f"⚠️  Allergies: {len(allergies)}")
        print(f"📱 Devices: {len(devices)}")
        print(f"🚑 Emergency Access: {len(emergency_records)}")
        print(f"📝 Audit Logs: ~3,000")
        print("=" * 70)
        print("\n✅ Realistic data seeding complete!")
        print("\n📘 Login Credentials:")
        print("   Admins: admin1/Admin@123, admin2/Admin@123")
        print("   Doctors: dr_smith/Doctor@123, dr_johnson/Doctor@123, ...")
        print("   Patients: (username format: firstname.lastname#)/Patient@123")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🏥 REALISTIC LARGE-SCALE DATA SEEDER")
    print("=" * 70)
    print("\n⚠️  WARNING: This will create 100 patients and ~1,200 vitals")
    print("   This may take 30-60 seconds to complete.\n")
    
    response = input("Continue? (y/n): ").strip().lower()
    
    if response == 'y':
        # Recreate tables
        print("\n🗄️  Recreating database tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables recreated\n")
        
        # Seed data
        seed_large_realistic_data()
        
        print("\n🎉 Done! Start the server and test with the credentials above.")
    else:
        print("\n❌ Cancelled.")
