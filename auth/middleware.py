from flask import request, current_app, g
from functools import wraps
import time
from datetime import datetime, timedelta
from models import SecurityLog
from extensions import db


class SecurityMiddleware:
    """Security middleware for additional protection"""
    
    def __init__(self, app):
        self.app = app
        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        self.app.errorhandler(404)(self.handle_404)
        self.app.errorhandler(500)(self.handle_500)
    
    def before_request(self):
        """Security checks before each request"""
        g.start_time = time.time()
        
        # Check for blocked IPs
        if self.is_ip_blocked(request.remote_addr):
            return self.block_request("IP address is blocked")
        
        # Check for suspicious user agents
        if self.is_suspicious_user_agent(request.headers.get('User-Agent')):
            self.log_suspicious_activity('suspicious_user_agent', request.remote_addr)
        
        # Check for suspicious request patterns
        if self.is_suspicious_request(request):
            self.log_suspicious_activity('suspicious_request_pattern', request.remote_addr)
        
        # Rate limiting for sensitive endpoints
        if self.should_rate_limit(request):
            if self.is_rate_limited(request.remote_addr, request.endpoint):
                return self.block_request("Rate limit exceeded")
    
    def after_request(self, response):
        """Security headers and logging after each request"""
        # Add security headers with development-friendly settings
        if current_app.config.get('DEBUG', False):
            # More permissive headers for development
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'SAMEORIGIN',
                'X-XSS-Protection': '1; mode=block',
            }
        else:
            # Strict headers for production
            security_headers = current_app.config.get('SECURITY_HEADERS', {})
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Add custom security headers
        response.headers['X-Request-ID'] = self.generate_request_id()
        response.headers['X-Response-Time'] = self.calculate_response_time()
        
        # Log request details for security monitoring
        self.log_request_details(request, response)
        
        return response
    
    def is_ip_blocked(self, ip_address):
        """Check if IP address is blocked"""
        blocked_ips = current_app.config.get('BLOCKED_IPS', [])
        return ip_address in blocked_ips
    
    def is_suspicious_user_agent(self, user_agent):
        """Check if user agent is suspicious"""
        if not user_agent:
            return True
        
        suspicious_patterns = [
            'bot', 'crawler', 'spider', 'scanner', 'curl', 'wget',
            'python-requests', 'go-http-client', 'java-http-client',
            'sqlmap', 'nikto', 'nmap', 'burp', 'zap'
        ]
        
        return any(pattern in user_agent.lower() for pattern in suspicious_patterns)
    
    def is_suspicious_request(self, request):
        """Check for suspicious request patterns"""
        # Check for SQL injection attempts
        sql_patterns = [
            'union select', 'drop table', 'delete from', 'insert into',
            'update set', 'alter table', 'exec(', 'eval('
        ]
        
        # Check for XSS attempts
        xss_patterns = [
            '<script', 'javascript:', 'vbscript:', 'onload=',
            'onerror=', 'onclick=', 'onmouseover='
        ]
        
        # Check request data
        request_data = str(request.values) + str(request.headers)
        request_data_lower = request_data.lower()
        
        for pattern in sql_patterns + xss_patterns:
            if pattern in request_data_lower:
                return True
        
        return False
    
    def should_rate_limit(self, request):
        """Determine if request should be rate limited"""
        sensitive_endpoints = [
            'auth.login', 'auth.register', 'auth.password_reset_request'
        ]
        return request.endpoint in sensitive_endpoints
    
    def is_rate_limited(self, ip_address, endpoint):
        """Check if IP is rate limited for specific endpoint"""
        # This would integrate with Flask-Limiter
        # For now, basic implementation
        return False
    
    def block_request(self, reason):
        """Block suspicious request"""
        self.log_suspicious_activity('request_blocked', request.remote_addr, reason)
        return {'error': 'Request blocked for security reasons'}, 403
    
    def log_suspicious_activity(self, activity_type, ip_address, details=None):
        """Log suspicious activity"""
        try:
            security_log = SecurityLog(
                event_type=activity_type,
                ip_address=ip_address,
                user_agent=request.headers.get('User-Agent'),
                details=details or f'Suspicious activity from {ip_address}',
                severity='warning',
                timestamp=datetime.utcnow()
            )
            
            db.session.add(security_log)
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Failed to log suspicious activity: {e}")
    
    def log_request_details(self, request, response):
        """Log request details for security monitoring"""
        try:
            # Only log sensitive requests
            if request.endpoint in ['auth.login', 'auth.register', 'auth.password_reset']:
                security_log = SecurityLog(
                    event_type='request_logged',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent'),
                    details=f'{request.method} {request.endpoint} - Status: {response.status_code}',
                    severity='info',
                    timestamp=datetime.utcnow()
                )
                
                db.session.add(security_log)
                db.session.commit()
                
        except Exception as e:
            current_app.logger.error(f"Failed to log request details: {e}")
    
    def generate_request_id(self):
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def calculate_response_time(self):
        """Calculate response time"""
        if hasattr(g, 'start_time'):
            return f"{(time.time() - g.start_time) * 1000:.2f}ms"
        return "0ms"
    
    def handle_404(self, error):
        """Handle 404 errors securely"""
        # Don't reveal internal structure
        return {'error': 'Page not found'}, 404
    
    def handle_500(self, error):
        """Handle 500 errors securely"""
        # Log the error for debugging
        current_app.logger.error(f"Internal server error: {error}")
        
        # Don't reveal internal errors to users
        return {'error': 'Internal server error'}, 500


def require_https(f):
    """Decorator to require HTTPS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and not current_app.debug:
            return {'error': 'HTTPS required'}, 403
        return f(*args, **kwargs)
    return decorated_function


def require_secure_headers(f):
    """Decorator to require secure headers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for secure headers
        if not request.headers.get('X-Forwarded-Proto') == 'https' and not current_app.debug:
            return {'error': 'Secure connection required'}, 403
        return f(*args, **kwargs)
    return decorated_function


def log_security_event(event_type, details, severity='info', user_id=None):
    """Helper function to log security events"""
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


def check_request_frequency(ip_address, window_minutes=15, max_requests=100):
    """Check if IP has made too many requests in a time window"""
    try:
        from models import SecurityLog
        
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        request_count = SecurityLog.query.filter(
            SecurityLog.ip_address == ip_address,
            SecurityLog.timestamp >= window_start,
            SecurityLog.event_type.in_(['request_logged', 'login_attempt'])
        ).count()
        
        return request_count > max_requests
        
    except Exception as e:
        current_app.logger.error(f"Failed to check request frequency: {e}")
        return False
