from extensions import db
from flask_login import UserMixin
from datetime import datetime, timezone


class User(UserMixin, db.Model):
    __tablename__ = 'users'   # 👈 Add this line

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class LoginAttempt(db.Model):
    """Track login attempts for security monitoring"""
    __tablename__ = "login_attempts"
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv6 compatible
    user_agent = db.Column(db.String(500))
    email = db.Column(db.String(120))
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    failure_reason = db.Column(db.String(100))
    
    # Additional security fields
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)


class SecurityLog(db.Model):
    """Log security-related events"""
    __tablename__ = "security_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_type = db.Column(db.String(50), nullable=False)  # login, logout, password_change, etc.
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default='info')  # info, warning, critical

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class CareerApplication(db.Model):
    __tablename__ = "career_applications"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    position_type = db.Column(db.String(50), nullable=False)  # Internship or Job
    department = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    resume_filename = db.Column(db.String(255))  # store file name
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))  # store image path
    category = db.Column(db.String(100))  # e.g. Wedding, Corporate
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    

    def __repr__(self):
        return f"<Event {self.title}>"
