"""
Authentication middleware for KidQuest application.
This module provides decorators for JWT authentication and role-based access control.
"""
from functools import wraps
from flask import request, jsonify, g
import time
from services.jwt_service import validate_access_token
from services.rbac_service import has_role, has_permission

def jwt_required(f):
    """
    Decorator to require JWT authentication for a route.
    
    Args:
        f (function): The route function to decorate
        
    Returns:
        function: Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Check if the header is in the correct format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'success': False, 'error': 'Invalid authorization header format'}), 401
        
        token = parts[1]
        
        # Validate the token
        payload = validate_access_token(token)
        if not payload:
            return jsonify({'success': False, 'error': 'Invalid or expired token'}), 401
        
        # Store user info in the request context
        g.user = {
            'id': payload.get('sub'),
            'role': payload.get('role')
        }
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """
    Decorator to require a specific role for a route.
    Must be used after jwt_required.
    
    Args:
        required_role (str): The required role ('admin', 'teacher', 'parent', 'child')
        
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            
            user_role = g.user.get('role')
            
            # Check if user has the required role
            if not has_role(user_role, required_role):
                return jsonify({
                    'success': False, 
                    'error': 'Insufficient permissions',
                    'required_role': required_role
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(resource, action):
    """
    Decorator to require a specific permission for a route.
    Must be used after jwt_required.
    
    Args:
        resource (str): The resource being accessed ('profile', 'chat', etc.)
        action (str): The action being performed ('read_own', 'update_all', etc.)
        
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not hasattr(g, 'user') or not g.user:
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            
            user_role = g.user.get('role')
            
            # Check if user has the required permission
            if not has_permission(user_role, resource, action):
                return jsonify({
                    'success': False, 
                    'error': 'Insufficient permissions',
                    'resource': resource,
                    'action': action
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Simple in-memory rate limiting
rate_limit_data = {}

def rate_limit(max_attempts=5, window=300, key_func=None):
    """
    Decorator to apply rate limiting to a route.
    
    Args:
        max_attempts (int): Maximum number of attempts allowed in the time window
        window (int): Time window in seconds
        key_func (function): Function to generate the rate limit key (defaults to IP address)
        
    Returns:
        function: Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the rate limit key
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr
                
            current_time = time.time()
            
            # Initialize or clean up rate limit data for this key
            if key not in rate_limit_data:
                rate_limit_data[key] = []
            
            # Remove attempts outside the current window
            rate_limit_data[key] = [t for t in rate_limit_data[key] if current_time - t < window]
            
            # Check if the rate limit has been exceeded
            if len(rate_limit_data[key]) >= max_attempts:
                return jsonify({
                    'success': False, 
                    'error': 'Rate limit exceeded',
                    'retry_after': int(window - (current_time - rate_limit_data[key][0]))
                }), 429
            
            # Add the current attempt
            rate_limit_data[key].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator