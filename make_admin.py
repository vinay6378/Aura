#!/usr/bin/env python3
"""
Simple script to convert existing user to admin
"""

import sqlite3
import os

def make_user_admin():
    """Convert the existing user to admin"""
    
    # Database path
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("👑 Converting user to admin...")
        print("=" * 40)
        
        # Get existing user
        cursor.execute("SELECT id, username, email FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("❌ No users found in database")
            return False
        
        user_id, username, email = user
        print(f"👤 Found user: {username} ({email})")
        
        # Convert to admin
        cursor.execute("""
            UPDATE users 
            SET is_admin = 1, role = 'admin'
            WHERE id = ?
        """, (user_id,))
        
        conn.commit()
        print(f"🎉 User {username} is now an admin!")
        
        # Verify the change
        cursor.execute("SELECT username, email, is_admin, role FROM users WHERE id = ?", (user_id,))
        updated_user = cursor.fetchone()
        username, email, is_admin, role = updated_user
        
        print(f"\n✅ Admin status confirmed:")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Is Admin: {'✅ Yes' if is_admin else '❌ No'}")
        print(f"   Role: {role}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    make_user_admin()
