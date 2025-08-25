#!/usr/bin/env python3
"""
Script to create an admin user in the Aura database
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

def create_admin_user(email, username, password, is_super_admin=True):
    """Create an admin user in the database"""
    
    # Database path
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"👑 Creating admin user: {username}")
        print("=" * 50)
        
        # Check if user already exists
        cursor.execute("SELECT id, username, is_admin FROM users WHERE email = ?", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id, existing_username, is_admin = existing_user
            print(f"✅ User already exists: {existing_username} (ID: {user_id})")
            
            if is_admin:
                print("👑 User is already an admin!")
                return True
            
            # Convert existing user to admin
            print("🔄 Converting existing user to admin...")
            cursor.execute("""
                UPDATE users 
                SET is_admin = 1, role = 'admin', updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (email,))
            
            conn.commit()
            print(f"🎉 User {existing_username} is now an admin!")
            return True
        
        # Create new admin user
        print("🆕 Creating new admin user...")
        
        # Generate password hash
        password_hash = generate_password_hash(password, method='pbkdf2:sha256:600000')
        
        # Insert new admin user
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, is_admin, role, 
                email_verified, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, 1, 'admin', 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (username, email, password_hash))
        
        # Commit changes
        conn.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"👤 Username: {username}")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👑 Role: Admin")
        print(f"🔒 Password hash: {password_hash[:30]}...")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def check_admin_users():
    """Check all admin users in the database"""
    
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("👑 Checking admin users...")
        print("=" * 40)
        
        # Check if is_admin column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'is_admin' not in columns:
            print("❌ Admin column not found. Adding it...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'")
            cursor.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
            conn.commit()
            print("✅ Admin columns added!")
        
        # Get all admin users
        cursor.execute("""
            SELECT id, username, email, is_admin, role, created_at, updated_at
            FROM users 
            WHERE is_admin = 1 OR role = 'admin'
            ORDER BY id
        """)
        
        admin_users = cursor.fetchone()
        
        if not admin_users:
            print("❌ No admin users found")
            return
        
        print(f"✅ Found admin user:")
        user_id, username, email, is_admin, role, created_at, updated_at = admin_users
        
        print(f"👤 User ID: {user_id}")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Is Admin: {'✅ Yes' if is_admin else '❌ No'}")
        print(f"   Role: {role}")
        print(f"   Created: {created_at}")
        print(f"   Updated: {updated_at}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking admin users: {e}")

def main():
    """Main function to create admin user"""
    print("👑 Aura Admin User Creation Tool")
    print("=" * 40)
    
    print("\nChoose an option:")
    print("1. Create new admin user")
    print("2. Convert existing user to admin")
    print("3. Check current admin users")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        print("\n🆕 Creating new admin user...")
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = input("Enter password: ").strip()
        confirm_password = input("Confirm password: ").strip()
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        if create_admin_user(email, username, password):
            print("\n🎉 Admin user created successfully!")
        else:
            print("\n❌ Failed to create admin user!")
    
    elif choice == "2":
        print("\n🔄 Converting existing user to admin...")
        email = input("Enter user email: ").strip()
        
        if create_admin_user(email, "", "", True):
            print("\n🎉 User converted to admin successfully!")
        else:
            print("\n❌ Failed to convert user!")
    
    elif choice == "3":
        check_admin_users()
    
    elif choice == "4":
        print("👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
