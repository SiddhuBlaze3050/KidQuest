"""
JWT service for KidQuest application.
This module provides JWT token generation, validation, and refresh functionality.
"""
import jwt
import uuid
import hashlib
from datetime import datetime, timedelta
from flask import current_app
from models import db, User, TokenBlacklist, RefreshToken

def generate_access_token(user):
    """
    Generate a JWT access token for a user.
    
    Args:
        user (User): The user object
        
    Returns:
        str: JWT access token
    """
    now = datetime.utcnow()
    token_jti = str(uuid.uuid4())
    
    # Set token expiration (default: 30 minutes)
    expiration = now + timedelta(seconds=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 1800))
    
    # Create token payload
    payload = {
        'sub': user.id,
        'role': user.role,
        'iat': now,
        'exp': expiration,
        'jti': token_jti
    }
    
    # Generate token
    token = jwt.encode(
        payload,
        current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production'),
        algorithm=current_app.config.get('JWT_ALGORITHM', 'HS256')
    )
    
    return token

def generate_refresh_token(user):
    """
    Generate a refresh token for a user and store it in the database.
    
    Args:
        user (User): The user object
        
    Returns:
        str: Refresh token
    """
    # Generate a random token
    token = str(uuid.uuid4())
    
    # Hash the token for storage
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Set token expiration (default: 30 days)
    expires_at = datetime.utcnow() + timedelta(seconds=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # Store the token in the database
    refresh_token = RefreshToken(
        token_hash=token_hash,
        user_id=user.id,
        expires_at=expires_at
    )
    
    db.session.add(refresh_token)
    db.session.commit()
    
    return token

def validate_access_token(token):
    """
    Validate a JWT access token.
    
    Args:
        token (str): JWT access token
        
    Returns:
        dict: Token payload if valid, None otherwise
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            current_app.config.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production'),
            algorithms=[current_app.config.get('JWT_ALGORITHM', 'HS256')]
        )
        
        # Check if token is blacklisted
        token_jti = payload.get('jti')
        blacklisted = TokenBlacklist.query.filter_by(token_jti=token_jti).first()
        if blacklisted:
            return None
        
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def refresh_access_token(refresh_token):
    """
    Refresh an access token using a refresh token.
    
    Args:
        refresh_token (str): Refresh token
        
    Returns:
        tuple: (new_access_token, new_refresh_token) if valid, (None, None) otherwise
    """
    # Hash the token for lookup
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    
    # Look up the token in the database
    stored_token = RefreshToken.query.filter_by(
        token_hash=token_hash,
        is_revoked=False
    ).first()
    
    if not stored_token:
        return None, None
    
    # Check if token is expired
    if stored_token.expires_at < datetime.utcnow():
        stored_token.is_revoked = True
        db.session.commit()
        return None, None
    
    # Get the user
    user = User.query.get(stored_token.user_id)
    if not user:
        return None, None
    
    # Revoke the old refresh token
    stored_token.is_revoked = True
    db.session.commit()
    
    # Generate new tokens
    new_access_token = generate_access_token(user)
    new_refresh_token = generate_refresh_token(user)
    
    return new_access_token, new_refresh_token

def blacklist_token(token):
    """
    Blacklist a JWT token.
    
    Args:
        token (str): JWT token to blacklist
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Decode the token without verification to get the payload
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        # Extract token data
        token_jti = payload.get('jti')
        user_id = payload.get('sub')
        expires_at = datetime.fromtimestamp(payload.get('exp'))
        
        # Check if token is already blacklisted
        existing = TokenBlacklist.query.filter_by(token_jti=token_jti).first()
        if existing:
            return True
        
        # Add token to blacklist
        blacklisted_token = TokenBlacklist(
            token_jti=token_jti,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.session.add(blacklisted_token)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error blacklisting token: {str(e)}")
        db.session.rollback()
        return False

def revoke_all_user_tokens(user_id):
    """
    Revoke all refresh tokens for a user.
    
    Args:
        user_id (int): User ID
        
    Returns:
        int: Number of tokens revoked
    """
    try:
        # Mark all refresh tokens as revoked
        result = RefreshToken.query.filter_by(
            user_id=user_id,
            is_revoked=False
        ).update({'is_revoked': True})
        
        db.session.commit()
        return result
    except Exception as e:
        current_app.logger.error(f"Error revoking user tokens: {str(e)}")
        db.session.rollback()
        return 0