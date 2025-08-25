#!/usr/bin/env python3
"""
Quick script to check user credentials in the Aura database
"""

import sqlite3
import os
from datetime import datetime

def check_users():
    """Check all users in the database"""
    
    # Database path
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking users in Aura database...")
        print("=" * 60)
        
        # Get all users
        cursor.execute("""
            SELECT id, username, email, password_hash, created_at, 
                   email_verified, is_active, is_suspended,
                   failed_login_attempts, last_login
            FROM users
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("❌ No users found in database")
            return
        
        print(f"✅ Found {len(users)} user(s):")
        print()
        
        for user in users:
            user_id, username, email, password_hash, created_at, email_verified, is_active, is_suspended, failed_attempts, last_login = user
            
            print(f"👤 User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Password Hash: {password_hash[:20]}...")
            print(f"   Created: {created_at}")
            print(f"   Email Verified: {'✅ Yes' if email_verified else '❌ No'}")
            print(f"   Active: {'✅ Yes' if is_active else '❌ No'}")
            print(f"   Suspended: {'❌ Yes' if is_suspended else '✅ No'}")
            print(f"   Failed Login Attempts: {failed_attempts}")
            print(f"   Last Login: {last_login or 'Never'}")
            print("-" * 40)
        
        # Check login attempts
        print("\n📊 Recent Login Attempts:")
        cursor.execute("""
            SELECT email, success, timestamp, ip_address, failure_reason
            FROM login_attempts
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        attempts = cursor.fetchall()
        
        if attempts:
            for attempt in attempts:
                email, success, timestamp, ip, reason = attempt
                status = "✅ Success" if success else "❌ Failed"
                print(f"   {email} - {status} at {timestamp} from {ip}")
                if not success and reason:
                    print(f"     Reason: {reason}")
        else:
            print("   No login attempts recorded yet")
        
        # Check security logs
        print("\n🔒 Recent Security Events:")
        cursor.execute("""
            SELECT event_type, timestamp, details, severity
            FROM security_logs
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        events = cursor.fetchall()
        
        if events:
            for event in events:
                event_type, timestamp, details, severity = event
                print(f"   {event_type} - {severity.upper()} at {timestamp}")
                if details:
                    print(f"     Details: {details}")
        else:
            print("   No security events recorded yet")
        
        conn.close()
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_users()
