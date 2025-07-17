"""
JWT Authentication module for KidQuest application.
This module provides JWT token generation, validation, and RBAC functionality.
"""
from flask import request, jsonify, g
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash
from models import db, User, TokenBlacklist, RefreshToken
from services.jwt_service import generate_access_token, generate_refresh_token, refresh_access_token, blacklist_token, revoke_all_user_tokens
from middleware.auth_middleware import jwt_required, role_required, permission_required, rate_limit

def init_jwt_auth(app):
    """
    Initialize JWT authentication for the Flask app.
    
    Args:
        app: Flask application instance
    """
    # Register JWT authentication routes
    
    @app.route('/api/auth/login', methods=['POST'])
    @rate_limit(max_attempts=10, window=60)
    def api_jwt_login():
        """API endpoint for user login with JWT token generation"""
        try:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({'success': False, 'error': 'Missing username or password'}), 400

            user = User.query.filter_by(username=username).first()
            if not user:
                # Don't reveal that the user doesn't exist
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
                
            # Secure password checking without logging sensitive information
            try:
                password_match = check_password_hash(user.password_hash, password) if user else False
            except Exception as e:
                # Log error without revealing sensitive details
                print(f"Error during authentication: {type(e).__name__}")
                password_match = False
            
            if password_match:
                # Reset login attempts on successful login
                user.login_attempts = 0
                user.account_locked_until = None
                user.last_login = datetime.utcnow()
                
                # Generate JWT tokens
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)
                
                # Update login streak if the function exists in the app context
                if 'update_login_streak' in globals():
                    update_login_streak(user.id)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role
                    }
                }), 200
            else:
                # Increment login attempts
                user.login_attempts = (user.login_attempts or 0) + 1
                
                # Lock account after 5 failed attempts
                if user.login_attempts >= 5:
                    user.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
                    
                db.session.commit()
                
                # Check if account is locked
                if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                    lock_minutes = int((user.account_locked_until - datetime.utcnow()).total_seconds() / 60)
                    return jsonify({
                        'success': False, 
                        'error': f'Account temporarily locked. Try again in {lock_minutes} minutes.'
                    }), 403
                    
                return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/auth/refresh', methods=['POST'])
    def api_refresh_token():
        """API endpoint for refreshing JWT tokens"""
        try:
            data = request.get_json()
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return jsonify({'success': False, 'error': 'Refresh token is required'}), 400
            
            # Attempt to refresh the token
            new_access_token, new_refresh_token = refresh_access_token(refresh_token)
            
            if not new_access_token or not new_refresh_token:
                return jsonify({'success': False, 'error': 'Invalid or expired refresh token'}), 401
            
            return jsonify({
                'success': True,
                'access_token': new_access_token,
                'refresh_token': new_refresh_token
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/auth/logout', methods=['POST'])
    @jwt_required
    def api_logout():
        """API endpoint for user logout with token invalidation"""
        try:
            # Get the token from the Authorization header
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1] if auth_header else None
            
            # Get user ID from the request context (set by jwt_required decorator)
            user_id = g.user.get('id')
            
            # Blacklist the current access token
            if token:
                blacklist_token(token)
            
            # Optionally revoke all refresh tokens for the user
            data = request.get_json()
            revoke_all = data.get('revoke_all', False)
            
            if revoke_all:
                revoke_all_user_tokens(user_id)
                message = "Logged out from all devices"
            else:
                message = "Logged out successfully"
            
            return jsonify({
                'success': True,
                'message': message
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/auth/protected', methods=['GET'])
    @jwt_required
    def api_protected():
        """Test endpoint for JWT authentication"""
        return jsonify({
            'success': True,
            'message': 'You have access to this protected resource',
            'user_id': g.user.get('id'),
            'role': g.user.get('role')
        }), 200

    @app.route('/api/auth/admin', methods=['GET'])
    @jwt_required
    @role_required('admin')
    def api_admin_only():
        """Test endpoint for admin role"""
        return jsonify({
            'success': True,
            'message': 'You have admin access',
            'user_id': g.user.get('id')
        }), 200

    @app.route('/api/auth/parent', methods=['GET'])
    @jwt_required
    @role_required('parent')
    def api_parent_only():
        """Test endpoint for parent role"""
        return jsonify({
            'success': True,
            'message': 'You have parent access',
            'user_id': g.user.get('id')
        }), 200

    @app.route('/api/auth/child', methods=['GET'])
    @jwt_required
    @role_required('child')
    def api_child_only():
        """Test endpoint for child role"""
        return jsonify({
            'success': True,
            'message': 'You have child access',
            'user_id': g.user.get('id')
        }), 200

    @app.route('/api/auth/teacher', methods=['GET'])
    @jwt_required
    @role_required('teacher')
    def api_teacher_only():
        """Test endpoint for teacher role"""
        return jsonify({
            'success': True,
            'message': 'You have teacher access',
            'user_id': g.user.get('id')
        }), 200
        
    # Return the app with JWT routes registered
    return app