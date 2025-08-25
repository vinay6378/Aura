#!/usr/bin/env python3
"""
Check what columns exist in the users table
"""

import sqlite3
import os

def check_columns():
    """Check existing columns in users table"""
    
    db_path = os.path.join('instance', 'aura.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking users table structure...")
        print("=" * 40)
        
        # Get table info
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"📋 Found {len(columns)} columns:")
        for col in columns:
            col_id, name, type_name, not_null, default_val, primary_key = col
            print(f"   {name} ({type_name}) - Default: {default_val}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_columns()
