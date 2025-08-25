#!/usr/bin/env python3
"""
Aura Security System Setup Script
This script helps you set up the enhanced security features
"""

import os
import sys
import subprocess

def check_dependencies():
    """Check if required packages are installed"""
    print("Checking dependencies...")
    
    required_packages = [
        'Flask', 'Flask-SQLAlchemy', 'Flask-Login', 'Flask-Limiter', 
        'Flask-WTF', 'WTForms', 'email-validator', 'bcrypt', 'PyJWT', 'cryptography'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("All dependencies are installed!")
    return True

def setup_database():
    """Set up the database with security features"""
    print("\nSetting up database...")
    
    if os.path.exists('migrate_db.py'):
        try:
            result = subprocess.run([sys.executable, 'migrate_db.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Database migration completed successfully!")
                return True
            else:
                print(f"✗ Database migration failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error running migration: {e}")
            return False
    else:
        print("✗ Migration script not found")
        return False

def create_env_file():
    """Create a .env file with security configuration"""
    print("\nCreating environment configuration...")
    
    env_content = """# Aura Security Configuration
# Copy this to .env and update with your values

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///instance/aura.db

# Email Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Security Configuration
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8
BLOCKED_IPS=

# Production Settings (uncomment for production)
# FLASK_ENV=production
# SESSION_COOKIE_SECURE=true
# SESSION_COOKIE_HTTPONLY=true
"""
    
    try:
        with open('.env.example', 'w') as f:
            f.write(env_content)
        print("✓ Created .env.example file")
        print("  Copy it to .env and update with your values")
        return True
    except Exception as e:
        print(f"✗ Error creating .env file: {e}")
        return False

def verify_setup():
    """Verify that the security system is properly set up"""
    print("\nVerifying setup...")
    
    checks = [
        ("Database migration script", os.path.exists('migrate_db.py')),
        ("Configuration file", os.path.exists('config.py')),
        ("Security middleware", os.path.exists('auth/middleware.py')),
        ("Security forms", os.path.exists('auth/forms.py')),
        ("Security templates", os.path.exists('templates/auth/login.html')),
        ("Requirements file", os.path.exists('requirements.txt')),
    ]
    
    all_good = True
    for check_name, exists in checks:
        status = "✓" if exists else "✗"
        print(f"{status} {check_name}")
        if not exists:
            all_good = False
    
    return all_good

def main():
    """Main setup function"""
    print("Aura Security System Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies first.")
        return
    
    # Create environment file
    create_env_file()
    
    # Set up database
    if not setup_database():
        print("\nDatabase setup failed. Please check the error messages above.")
        return
    
    # Verify setup
    if not verify_setup():
        print("\nSetup verification failed. Some files are missing.")
        return
    
    print("\n" + "=" * 40)
    print("🎉 Security system setup completed successfully!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and update with your values")
    print("2. Run the application: python app.py")
    print("3. Visit http://localhost:5000 to test the security features")
    print("\nSecurity features available:")
    print("• Enhanced login/registration with password strength validation")
    print("• Rate limiting and account lockout protection")
    print("• Two-factor authentication support")
    print("• Comprehensive security logging and monitoring")
    print("• XSS and SQL injection protection")
    print("• CSRF protection and secure headers")

if __name__ == "__main__":
    main()
