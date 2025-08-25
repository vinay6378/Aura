import re
import hashlib
import ipaddress
from datetime import datetime, timedelta
from flask import request, current_app
from models import LoginAttempt, SecurityLog, User
from extensions import db
from urllib.parse import urlparse


class SecurityManager:
    """Manages security-related operations"""
    
    @staticmethod
    def is_safe_redirect(target):
        """Check if redirect target is safe (same domain)"""
        if not target:
            return False
        
        try:
            target_url = urlparse(target)
            request_url = urlparse(request.url)
            
            # Only allow redirects to same domain
            return target_url.netloc == request_url.netloc or not target_url.netloc
        except Exception:
            return False
    
    @staticmethod
    def is_suspicious_ip(ip_address):
        """Check if IP address is suspicious"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Check for private/local IPs (potential proxy/VPN)
            if ip.is_private or ip.is_loopback:
                return True
                
            # Check for known malicious IP ranges (example)
            malicious_ranges = [
                # Add known malicious IP ranges here
            ]
            
            for ip_range in malicious_ranges:
                if ip in ipaddress.ip_network(ip_range):
                    return True
                    
            return False
        except ValueError:
            return True
    
    @staticmethod
    def is_suspicious_user_agent(user_agent):
        """Check if user agent is suspicious"""
        if not user_agent:
            return True
            
        suspicious_patterns = [
            r'bot',
            r'crawler',
            r'spider',
            r'scanner',
            r'curl',
            r'wget',
            r'python-requests',
            r'go-http-client',
            r'java-http-client'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, user_agent.lower()):
                return True
                
        return False
    
    @staticmethod
    def log_login_attempt(email, success, failure_reason=None):
        """Log login attempt for security monitoring"""
        try:
            login_attempt = LoginAttempt(
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                email=email,
                success=success,
                failure_reason=failure_reason,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(login_attempt)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to log login attempt: {e}")
    
    @staticmethod
    def log_security_event(user_id, event_type, details, severity='info'):
        """Log security-related events"""
        try:
            security_log = SecurityLog(
                user_id=user_id,
                event_type=event_type,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                details=details,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(security_log)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to log security event: {e}")
    
    @staticmethod
    def check_rate_limit(ip_address, action, max_attempts, window_minutes):
        """Check if rate limit is exceeded for an action"""
        try:
            window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            attempts = LoginAttempt.query.filter(
                LoginAttempt.ip_address == ip_address,
                LoginAttempt.timestamp >= window_start
            ).count()
            
            return attempts >= max_attempts
            
        except Exception as e:
            current_app.logger.error(f"Failed to check rate limit: {e}")
            return False
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize user input to prevent XSS"""
        if not input_string:
            return input_string
            
        # Remove potentially dangerous HTML tags and attributes
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'onmouseover='
        ]
        
        sanitized = input_string
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
            
        return sanitized.strip()
    
    @staticmethod
    def generate_secure_token(length=32):
        """Generate a cryptographically secure token"""
        import secrets
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_sensitive_data(data):
        """Hash sensitive data for logging"""
        if not data:
            return None
        return hashlib.sha256(data.encode()).hexdigest()[:16]
