#!/usr/bin/env python3
"""
Database Migration Script for Aura Security Features
This script adds new security columns to the existing users table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the existing database to include new security columns"""
    
    # Database path
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Please run the application first to create the database")
        return False
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"Existing columns: {columns}")
        
        # New security columns to add
        new_columns = [
            ('email_verified', 'BOOLEAN DEFAULT 0'),
            ('email_verification_token', 'VARCHAR(255)'),
            ('email_verification_expires', 'DATETIME'),
            ('failed_login_attempts', 'INTEGER DEFAULT 0'),
            ('account_locked_until', 'DATETIME'),
            ('password_reset_token', 'VARCHAR(255)'),
            ('password_reset_expires', 'DATETIME'),
            ('two_factor_secret', 'VARCHAR(255)'),
            ('two_factor_enabled', 'BOOLEAN DEFAULT 0'),
            ('last_login', 'DATETIME'),
            ('last_password_change', 'DATETIME'),
            ('is_active', 'BOOLEAN DEFAULT 1'),
            ('is_suspended', 'BOOLEAN DEFAULT 0')
        ]
        
        # Add new columns if they don't exist
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                    print(f"Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"Column {column_name} already exists")
                    else:
                        print(f"Error adding column {column_name}: {e}")
            else:
                print(f"Column {column_name} already exists")
        
        # Create new security tables
        print("\nCreating security tables...")
        
        # LoginAttempt table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address VARCHAR(45) NOT NULL,
                user_agent VARCHAR(500),
                email VARCHAR(120),
                success BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                failure_reason VARCHAR(100),
                country VARCHAR(100),
                city VARCHAR(100),
                latitude REAL,
                longitude REAL
            )
        """)
        print("Created login_attempts table")
        
        # SecurityLog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type VARCHAR(50) NOT NULL,
                ip_address VARCHAR(45),
                user_agent VARCHAR(500),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                severity VARCHAR(20) DEFAULT 'info',
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        print("Created security_logs table")
        
        # Update existing users to have default values
        print("\nUpdating existing users...")
        
        # Set default values for existing users
        cursor.execute("""
            UPDATE users SET 
                email_verified = 1,
                failed_login_attempts = 0,
                two_factor_enabled = 0,
                is_active = 1,
                is_suspended = 0,
                last_password_change = ?
            WHERE email_verified IS NULL
        """, (datetime.utcnow(),))
        
        updated_rows = cursor.rowcount
        print(f"Updated {updated_rows} existing users with default values")
        
        # Commit changes
        conn.commit()
        print("\nDatabase migration completed successfully!")
        
        # Verify the new structure
        cursor.execute("PRAGMA table_info(users)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\nFinal users table columns: {final_columns}")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
        print("Database connection closed")

def create_indexes():
    """Create indexes for better performance"""
    
    db_path = os.path.join('instance', 'aura.db')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\nCreating indexes...")
        
        # Indexes for security tables
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_ip ON login_attempts(ip_address)",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_timestamp ON login_attempts(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_security_logs_user_id ON security_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_security_logs_event_type ON security_logs(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_security_logs_timestamp ON security_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_users_email_verified ON users(email_verified)",
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"Created index: {index_sql.split('idx_')[1].split(' ON ')[0]}")
            except Exception as e:
                print(f"Index creation warning: {e}")
        
        conn.commit()
        print("Indexes created successfully!")
        
    except Exception as e:
        print(f"Index creation failed: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Aura Database Migration Script")
    print("=" * 40)
    
    success = migrate_database()
    
    if success:
        create_indexes()
        print("\n" + "=" * 40)
        print("Migration completed successfully!")
        print("You can now run the application with enhanced security features.")
    else:
        print("\n" + "=" * 40)
        print("Migration failed. Please check the error messages above.")
        print("You may need to delete the existing database and let Flask create a new one.")
