"""
RBAC (Role-Based Access Control) service for KidQuest application.
This module provides role-based permission checking and access control.
"""
from functools import wraps
from flask import request, jsonify, g
import jwt
from models import User, ParentChild

# Role hierarchy (higher number = higher privileges)
ROLE_HIERARCHY = {
    'child': 1,
    'parent': 2,
    'teacher': 3,
    'admin': 4
}

# Permission matrix for different resources
PERMISSION_MATRIX = {
    'profile': {
        'child': ['read_own', 'update_own'],
        'parent': ['read_own', 'update_own', 'read_children', 'update_children'],
        'teacher': ['read_own', 'update_own', 'read_students'],
        'admin': ['read_all', 'update_all']
    },
    'chat': {
        'child': ['read_own', 'create_own'],
        'parent': ['read_own', 'create_own', 'read_children'],
        'teacher': ['read_own', 'create_own', 'read_students'],
        'admin': ['read_all', 'create_all']
    },
    'health': {
        'child': ['read_own', 'update_own'],
        'parent': ['read_own', 'update_own', 'read_children'],
        'teacher': ['read_own', 'update_own', 'read_students'],
        'admin': ['read_all', 'update_all']
    },
    'finance': {
        'child': ['read_own', 'update_own'],
        'parent': ['read_own', 'update_own', 'read_children', 'update_children'],
        'teacher': ['read_own', 'update_own'],
        'admin': ['read_all', 'update_all']
    },
    'tasks': {
        'child': ['read_own', 'update_own'],
        'parent': ['read_own', 'update_own', 'read_children'],
        'teacher': ['read_own', 'update_own', 'read_students', 'update_students'],
        'admin': ['read_all', 'update_all']
    },
    'system': {
        'admin': ['read_all', 'update_all']
    },
    'users': {
        'admin': ['read_all', 'update_all', 'create_all', 'delete_all']
    }
}

def has_role(user_role, required_role):
    """
    Check if a user's role meets or exceeds the required role level.
    
    Args:
        user_role (str): The user's role ('child', 'parent', 'teacher', 'admin')
        required_role (str): The required role for access
        
    Returns:
        bool: True if user's role meets or exceeds the required role, False otherwise
    """
    if user_role not in ROLE_HIERARCHY or required_role not in ROLE_HIERARCHY:
        return False
    
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]

def has_permission(user_role, resource, action):
    """
    Check if a user's role has permission to perform an action on a resource.
    
    Args:
        user_role (str): The user's role ('child', 'parent', 'teacher', 'admin')
        resource (str): The resource being accessed ('profile', 'chat', etc.)
        action (str): The action being performed ('read_own', 'update_all', etc.)
        
    Returns:
        bool: True if the user has permission, False otherwise
    """
    if resource not in PERMISSION_MATRIX:
        return False
    
    if user_role not in ROLE_HIERARCHY:
        return False
    
    # Admin has all permissions
    if user_role == 'admin':
        return True
    
    # Check if the role has any permissions for this resource
    if user_role not in PERMISSION_MATRIX[resource]:
        return False
    
    # Check if the specific action is allowed
    return action in PERMISSION_MATRIX[resource][user_role]

def can_access_user_data(current_user_id, current_user_role, target_user_id):
    """
    Check if a user can access another user's data.
    
    Args:
        current_user_id (int): The ID of the user making the request
        current_user_role (str): The role of the user making the request
        target_user_id (int): The ID of the user whose data is being accessed
        
    Returns:
        bool: True if access is allowed, False otherwise
    """
    # Users can always access their own data
    if current_user_id == target_user_id:
        return True
    
    # Admins can access any user's data
    if current_user_role == 'admin':
        return True
    
    # Parents can access their children's data
    if current_user_role == 'parent':
        parent_child = ParentChild.query.filter_by(
            parent_id=current_user_id, 
            child_id=target_user_id
        ).first()
        return parent_child is not None
    
    # Teachers can access their students' data (simplified - would need a proper teacher-student relationship)
    if current_user_role == 'teacher':
        # In a real implementation, check teacher-student relationship
        # For now, return False as we don't have this relationship defined
        return False
    
    # By default, deny access
    return False