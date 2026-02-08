"""
Quick database verification and stats script.
Run this to see the current database statistics.
"""
import sqlite3
from tabulate import tabulate

def get_db_stats():
    """Get comprehensive database statistics."""
    conn = sqlite3.connect('healthcare.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("📊 DATABASE STATISTICS")
    print("=" * 80)
    
    # Table counts
    tables = [
        ('users', 'Users'),
        ('patients', 'Patients'),
        ('biometric_hashes', 'Biometric Hashes'),
        ('consents', 'Consents'),
        ('vitals', 'Vitals'),
        ('alerts', 'Alerts'),
        ('health_conditions', 'Health Conditions'),
        ('allergies', 'Allergies'),
        ('devices', 'Devices'),
        ('emergency_access', 'Emergency Access'),
        ('audit_logs', 'Audit Logs')
    ]
    
    stats = []
    for table_name, display_name in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        stats.append([display_name, count])
    
    print("\n📈 Record Counts:")
    print(tabulate(stats, headers=['Table', 'Count'], tablefmt='grid'))
    
    # User breakdown
    print("\n\n👥 User Distribution:")
    cursor.execute("""
        SELECT role, COUNT(*) as count
        FROM users
        GROUP BY role
        ORDER BY count DESC
    """)
    user_stats = cursor.fetchall()
    print(tabulate(user_stats, headers=['Role', 'Count'], tablefmt='grid'))
    
    # Patient conditions
    print("\n\n🩺 Patient Health Conditions:")
    cursor.execute("""
        SELECT condition_name, COUNT(*) as count, 
               ROUND(AVG(CASE severity WHEN 'mild' THEN 1 WHEN 'moderate' THEN 2 WHEN 'severe' THEN 3 END), 1) as avg_severity
        FROM health_conditions
        WHERE is_active = 1
        GROUP BY condition_name
        ORDER BY count DESC
    """)
    conditions = cursor.fetchall()
    print(tabulate(conditions, headers=['Condition', 'Count', 'Avg Severity (1-3)'], tablefmt='grid'))
    
    # Alert breakdown
    print("\n\n🚨 Alert Distribution by Severity:")
    cursor.execute("""
        SELECT severity, COUNT(*) as count
        FROM alerts
        GROUP BY severity
        ORDER BY 
            CASE severity 
                WHEN 'CRITICAL' THEN 1
                WHEN 'HIGH' THEN 2
                WHEN 'MEDIUM' THEN 3
                WHEN 'LOW' THEN 4
            END
    """)
    alerts = cursor.fetchall()
    print(tabulate(alerts, headers=['Severity', 'Count'], tablefmt='grid'))
    
    # Vital types
    print("\n\n📊 Vital Types Distribution:")
    cursor.execute("""
        SELECT vital_type, COUNT(*) as count, 
               ROUND(AVG(value), 1) as avg_value,
               unit
        FROM vitals
        GROUP BY vital_type
        ORDER BY count DESC
        LIMIT 10
    """)
    vitals = cursor.fetchall()
    print(tabulate(vitals, headers=['Vital Type', 'Count', 'Avg Value', 'Unit'], tablefmt='grid'))
    
    # Consent breakdown
    print("\n\n📜 Consent Status:")
    cursor.execute("""
        SELECT purpose, 
               SUM(CASE WHEN granted = 1 THEN 1 ELSE 0 END) as granted,
               SUM(CASE WHEN granted = 0 THEN 1 ELSE 0 END) as revoked
        FROM consents
        GROUP BY purpose
    """)
    consents = cursor.fetchall()
    print(tabulate(consents, headers=['Purpose', 'Granted', 'Revoked'], tablefmt='grid'))
    
    # Device types
    print("\n\n📱 Device Types:")
    cursor.execute("""
        SELECT device_type, COUNT(*) as count,
               SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active
        FROM devices
        GROUP BY device_type
    """)
    devices = cursor.fetchall()
    print(tabulate(devices, headers=['Device Type', 'Total', 'Active'], tablefmt='grid'))
    
    # Recent activity
    print("\n\n⏰ Recent Activity (Last 7 Days):")
    cursor.execute("""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as events
        FROM audit_logs
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY date DESC
        LIMIT 7
    """)
    activity = cursor.fetchall()
    print(tabulate(activity, headers=['Date', 'Audit Events'], tablefmt='grid'))
    
    # Critical patients
    print("\n\n🚨 Patients with Critical Alerts:")
    cursor.execute("""
        SELECT 
            p.first_name || ' ' || p.last_name as patient_name,
            COUNT(a.id) as critical_alerts
        FROM patients p
        JOIN alerts a ON p.id = a.patient_id
        WHERE a.severity = 'CRITICAL' AND a.resolved = 0
        GROUP BY p.id, p.first_name, p.last_name
        ORDER BY critical_alerts DESC
        LIMIT 10
    """)
    critical_patients = cursor.fetchall()
    if critical_patients:
        print(tabulate(critical_patients, headers=['Patient', 'Unresolved Critical Alerts'], tablefmt='grid'))
    else:
        print("   No unresolved critical alerts")
    
    # Allergen distribution
    print("\n\n⚠️  Top 10 Allergens:")
    cursor.execute("""
        SELECT allergen, COUNT(*) as count,
               SUM(CASE WHEN severity = 'severe' THEN 1 ELSE 0 END) as severe_cases
        FROM allergies
        WHERE is_active = 1
        GROUP BY allergen
        ORDER BY count DESC
        LIMIT 10
    """)
    allergens = cursor.fetchall()
    print(tabulate(allergens, headers=['Allergen', 'Cases', 'Severe'], tablefmt='grid'))
    
    print("\n" + "=" * 80)
    print("✅ Database verification complete!")
    print("=" * 80)
    
    conn.close()

if __name__ == "__main__":
    try:
        get_db_stats()
    except ImportError:
        print("⚠️  Installation required: pip install tabulate")
        print("   Running simplified version...\n")
        
        # Simplified version without tabulate
        import sqlite3
        conn = sqlite3.connect('healthcare.db')
        cursor = conn.cursor()
        
        print("DATABASE RECORD COUNTS:")
        tables = ['users', 'patients', 'biometric_hashes', 'consents', 'vitals', 
                  'alerts', 'health_conditions', 'allergies', 'devices', 
                  'emergency_access', 'audit_logs']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:20s}: {count:5d}")
        
        conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")
