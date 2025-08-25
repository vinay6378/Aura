#!/usr/bin/env python3
"""
Script to reset a user's password in the Aura database
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def reset_user_password(email, new_password):
    """Reset a user's password in the database"""
    
    # Database path
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"🔐 Resetting password for: {email}")
        print("=" * 50)
        
        # Check if user exists
        cursor.execute("SELECT id, username FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User with email {email} not found!")
            return False
        
        user_id, username = user
        print(f"✅ Found user: {username} (ID: {user_id})")
        
        # Generate new password hash
        new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256:600000')
        
        # Update password in database
        cursor.execute("""
            UPDATE users 
            SET password_hash = ?, last_password_change = CURRENT_TIMESTAMP
            WHERE email = ?
        """, (new_password_hash, email))
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Password updated successfully!")
        print(f"📝 New password: {new_password}")
        print(f"🔒 Password hash: {new_password_hash[:30]}...")
        print(f"⏰ Updated at: {datetime.now()}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def main():
    """Main function to reset password"""
    print("🔐 Aura Password Reset Tool")
    print("=" * 40)
    
    # Get user input
    email = input("Enter user email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    new_password = input("Enter new password: ").strip()
    if not new_password:
        print("❌ Password cannot be empty!")
        return
    
    # Confirm password
    confirm_password = input("Confirm new password: ").strip()
    if new_password != confirm_password:
        print("❌ Passwords don't match!")
        return
    
    # Validate password strength
    if len(new_password) < 8:
        print("⚠️  Warning: Password is less than 8 characters")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            print("❌ Password reset cancelled")
            return
    
    # Reset password
    if reset_user_password(email, new_password):
        print("\n🎉 Password reset completed!")
        print(f"📧 You can now login with: {email}")
        print(f"🔑 New password: {new_password}")
    else:
        print("\n❌ Password reset failed!")

if __name__ == "__main__":
    from datetime import datetime
    main()
