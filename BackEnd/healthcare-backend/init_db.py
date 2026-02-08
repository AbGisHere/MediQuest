"""
Database initialization script.
Creates all tables and optionally seeds test data.
"""
from app.database import Base, engine
from app.models import *  # Import all models
from sqlalchemy.orm import Session
from app.auth.password import hash_password
from app.services.biometric import hash_fingerprint
import uuid
from datetime import datetime, timezone, timedelta

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    
def seed_data():
    """Seed initial test data."""
    from app.database import SessionLocal
    db = SessionLocal()
    
    try:
        print("\n📊 Seeding test data...")
        
        # 1. Create sample users
        print("\n1. Creating users...")
        
        # Admin user
        admin = User(
            id=str(uuid.uuid4()),
            username="admin",
            email="admin@healthcare.com",
            password_hash=hash_password("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        
        # Doctor user
        doctor = User(
            id=str(uuid.uuid4()),
            username="dr_smith",
            email="smith@hospital.com",
            password_hash=hash_password("Doctor@123"),
            role=UserRole.DOCTOR,
            is_active=True
        )
        db.add(doctor)
        
        # Another doctor
        doctor2 = User(
            id=str(uuid.uuid4()),
            username="dr_jones",
            email="jones@hospital.com",
            password_hash=hash_password("Doctor@123"),
            role=UserRole.DOCTOR,
            is_active=True
        )
        db.add(doctor2)
        
        db.commit()
        print(f"   ✅ Created 3 users (admin, dr_smith, dr_jones)")
        
        # 2. Create sample patients
        print("\n2. Creating patients...")
        
        # Patient 1
        patient1 = Patient(
            id=str(uuid.uuid4()),
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime(1985, 5, 15),
            gender="male",
            blood_group="A+",
            email="john.doe@email.com",
            phone="+1234567890",
            country="USA",
            emergency_contact_name="Jane Doe",
            emergency_contact_phone="+1234567891",
            emergency_contact_relationship="Spouse",
            registered_by=doctor.id,
            is_active=True
        )
        db.add(patient1)
        
        # Patient 2
        patient2 = Patient(
            id=str(uuid.uuid4()),
            first_name="Sarah",
            last_name="Johnson",
            date_of_birth=datetime(1990, 8, 22),
            gender="female",
            blood_group="O+",
            email="sarah.johnson@email.com",
            phone="+1234567892",
            country="USA",
            emergency_contact_name="Mike Johnson",
            emergency_contact_phone="+1234567893",
            emergency_contact_relationship="Father",
            registered_by=doctor.id,
            is_active=True
        )
        db.add(patient2)
        
        # Patient 3 - Diabetic patient
        patient3 = Patient(
            id=str(uuid.uuid4()),
            first_name="Michael",
            last_name="Williams",
            date_of_birth=datetime(1975, 3, 10),
            gender="male",
            blood_group="B+",
            email="michael.williams@email.com",
            phone="+1234567894",
            country="India",
            emergency_contact_name="Lisa Williams",
            emergency_contact_phone="+1234567895",
            emergency_contact_relationship="Spouse",
            registered_by=doctor2.id,
            is_active=True
        )
        db.add(patient3)
        
        db.commit()
        print(f"   ✅ Created 3 patients")
        
        # 3. Create biometric hashes for patients
        print("\n3. Creating biometric identities...")
        
        bio1 = BiometricHash(
            patient_id=patient1.id,
            fingerprint_hash=hash_fingerprint(f"fingerprint_{patient1.id}")
        )
        db.add(bio1)
        
        bio2 = BiometricHash(
            patient_id=patient2.id,
            fingerprint_hash=hash_fingerprint(f"fingerprint_{patient2.id}")
        )
        db.add(bio2)
        
        bio3 = BiometricHash(
            patient_id=patient3.id,
            fingerprint_hash=hash_fingerprint(f"fingerprint_{patient3.id}")
        )
        db.add(bio3)
        
        db.commit()
        print(f"   ✅ Created 3 biometric hashes")
        
        # 4. Grant consents
        print("\n4. Creating consent records...")
        
        consent1 = Consent(
            patient_id=patient1.id,
            purpose=ConsentPurpose.TREATMENT,
            granted=True,
            granted_by=patient1.id,
            granted_to=doctor.id
        )
        db.add(consent1)
        
        consent2 = Consent(
            patient_id=patient2.id,
            purpose=ConsentPurpose.TREATMENT,
            granted=True,
            granted_by=patient2.id,
            granted_to=doctor.id
        )
        db.add(consent2)
        
        consent3 = Consent(
            patient_id=patient3.id,
            purpose=ConsentPurpose.TREATMENT,
            granted=True,
            granted_by=patient3.id,
            granted_to=doctor2.id
        )
        db.add(consent3)
        
        db.commit()
        print(f"   ✅ Created 3 consent records")
        
        # 5. Add health conditions
        print("\n5. Creating health conditions...")
        
        condition1 = HealthCondition(
            patient_id=patient3.id,
            condition_name="Type 2 Diabetes",
            diagnosed_date=datetime(2020, 1, 15, tzinfo=timezone.utc),
            diagnosed_by=doctor2.id,
            severity="moderate",
            notes="Patient on metformin 500mg twice daily",
            is_active=True
        )
        db.add(condition1)
        
        condition2 = HealthCondition(
            patient_id=patient3.id,
            condition_name="Hypertension",
            diagnosed_date=datetime(2019, 6, 20, tzinfo=timezone.utc),
            diagnosed_by=doctor2.id,
            severity="mild",
            notes="Stage 1 hypertension, monitoring",
            is_active=True
        )
        db.add(condition2)
        
        db.commit()
        print(f"   ✅ Created 2 health conditions")
        
        # 6. Add allergies
        print("\n6. Creating allergies...")
        
        allergy1 = Allergy(
            patient_id=patient1.id,
            allergen="Penicillin",
            reaction="Rash and itching",
            severity="moderate",
            diagnosed_date=datetime(2015, 3, 1, tzinfo=timezone.utc),
            diagnosed_by=doctor.id,
            is_active=True
        )
        db.add(allergy1)
        
        allergy2 = Allergy(
            patient_id=patient3.id,
            allergen="Peanuts",
            reaction="Anaphylaxis",
            severity="severe",
            diagnosed_date=datetime(2018, 7, 10, tzinfo=timezone.utc),
            diagnosed_by=doctor2.id,
            is_active=True
        )
        db.add(allergy2)
        
        db.commit()
        print(f"   ✅ Created 2 allergies")
        
        # 7. Add sample vitals
        print("\n7. Creating sample vitals...")
        
        now = datetime.now(timezone.utc)
        vitals_count = 0
        
        # Patient 1 - Normal vitals
        for i in range(5):
            vital = Vital(
                patient_id=patient1.id,
                vital_type="heart_rate",
                value=72 + i,
                unit="bpm",
                source="device",
                source_id=doctor.id,
                recorded_at=now - timedelta(days=i),
                uploaded_by=doctor.id
            )
            db.add(vital)
            vitals_count += 1
        
        # Patient 3 - Diabetic with some critical readings
        glucose_values = [95, 180, 320, 150, 280]  # Some critical values
        for i, glucose in enumerate(glucose_values):
            vital = Vital(
                patient_id=patient3.id,
                vital_type="glucose",
                value=glucose,
                unit="mg/dL",
                source="device",
                source_id=doctor2.id,
                recorded_at=now - timedelta(days=i),
                uploaded_by=doctor2.id
            )
            db.add(vital)
            vitals_count += 1
        
        # Patient 2 - SpO2 readings
        spo2_values = [98, 97, 96, 88, 95]  # One critical low value
        for i, spo2 in enumerate(spo2_values):
            vital = Vital(
                patient_id=patient2.id,
                vital_type="spo2",
                value=spo2,
                unit="%",
                source="wearable",
                source_id=doctor.id,
                recorded_at=now - timedelta(days=i),
                uploaded_by=doctor.id
            )
            db.add(vital)
            vitals_count += 1
        
        db.commit()
        print(f"   ✅ Created {vitals_count} vital records")
        
        # 8. Generate alerts based on vitals
        print("\n8. Generating alerts for critical vitals...")
        from app.services.alerts import AlertEngine
        
        # Get critical vitals
        critical_vitals = db.query(Vital).filter(
            (Vital.vital_type == "glucose") & (Vital.value > 300) |
            (Vital.vital_type == "spo2") & (Vital.value < 90)
        ).all()
        
        alerts_count = 0
        for vital in critical_vitals:
            AlertEngine.evaluate_vital(db, vital)
            alerts_count += 1
        
        print(f"   ✅ Generated {alerts_count} alerts")
        
        print("\n✅ Seed data created successfully!")
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print(f"👥 Users: 3 (1 admin, 2 doctors)")
        print(f"   - Username: admin, Password: Admin@123")
        print(f"   - Username: dr_smith, Password: Doctor@123")
        print(f"   - Username: dr_jones, Password: Doctor@123")
        print(f"\n🏥 Patients: 3")
        print(f"   - John Doe (healthy)")
        print(f"   - Sarah Johnson (low oxygen reading)")
        print(f"   - Michael Williams (diabetic with critical glucose)")
        print(f"\n🔐 Biometric Hashes: 3")
        print(f"📜 Consents: 3")
        print(f"🩺 Health Conditions: 2")
        print(f"⚠️  Allergies: 2")
        print(f"📊 Vitals: {vitals_count}")
        print(f"🚨 Alerts: {alerts_count}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("🏥 Universal Healthcare Backend - Database Initialization")
    print("="*60)
    
    # Create tables
    create_tables()
    
    # Ask user if they want to seed data
    response = input("\n❓ Would you like to seed test data? (y/n): ").strip().lower()
    
    if response == 'y':
        seed_data()
    else:
        print("\n✅ Database initialized without seed data.")
    
    print("\n🎉 Database initialization complete!")
    print("\n📝 Next steps:")
    print("   1. Start the server: uvicorn main:app --reload")
    print("   2. Access API docs: http://localhost:8000/docs")
    print("   3. Login with test credentials above")
