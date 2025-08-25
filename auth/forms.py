from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from models import User
import re


class SecureLoginForm(FlaskForm):
    """Secure login form with enhanced validation"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
    def validate_email(self, field):
        """Custom validation for email"""
        if field.data:
            # Check for suspicious patterns
            suspicious_patterns = [
                r'<script',
                r'javascript:',
                r'vbscript:',
                r'onload=',
                r'onerror=',
                r'<iframe',
                r'<object',
                r'<embed'
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, field.data, re.IGNORECASE):
                    raise ValidationError('Invalid email format detected')


class SecureRegisterForm(FlaskForm):
    """Secure registration form with strong password requirements"""
    username = StringField('Username', validators=[
        DataRequired(message='Username is required'),
        Length(min=3, max=30, message='Username must be between 3 and 30 characters'),
        Regexp(r'^[a-zA-Z0-9_-]+$', message='Username can only contain letters, numbers, underscores, and hyphens')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email is too long')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=12, message='Password must be at least 12 characters long'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
        )
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    accept_terms = BooleanField('I accept the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must accept the terms to continue')
    ])
    submit = SubmitField('Create Account')
    
    def validate_username(self, field):
        """Check if username is already taken"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, field):
        """Check if email is already registered"""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email is already registered. Please use a different email or try logging in.')
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'<iframe',
            r'<object',
            r'<embed'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, field.data, re.IGNORECASE):
                raise ValidationError('Invalid email format detected')
    
    def validate_password(self, field):
        """Enhanced password validation"""
        password = field.data
        
        # Check for common weak passwords
        weak_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey'
        ]
        
        if password.lower() in weak_passwords:
            raise ValidationError('This password is too common. Please choose a stronger password.')
        
        # Check for sequential characters
        if re.search(r'(.)\1{2,}', password):
            raise ValidationError('Password cannot contain repeated characters (e.g., aaa, 111).')
        
        # Check for keyboard patterns
        keyboard_patterns = [
            'qwerty', 'asdfgh', 'zxcvbn', '123456', '654321'
        ]
        
        for pattern in keyboard_patterns:
            if pattern in password.lower() or pattern[::-1] in password.lower():
                raise ValidationError('Password cannot contain keyboard patterns.')


class PasswordResetRequestForm(FlaskForm):
    """Form for requesting password reset"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    submit = SubmitField('Request Password Reset')


class PasswordResetForm(FlaskForm):
    """Form for resetting password"""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=12, message='Password must be at least 12 characters long'),
        Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
            message='Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
        )
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class TwoFactorForm(FlaskForm):
    """Form for two-factor authentication"""
    code = StringField('Authentication Code', validators=[
        DataRequired(message='Authentication code is required'),
        Length(min=6, max=6, message='Code must be 6 digits'),
        Regexp(r'^\d{6}$', message='Code must contain only numbers')
    ])
    submit = SubmitField('Verify')
