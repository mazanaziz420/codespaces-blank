from flask import jsonify
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from utils import HttpCodes


def validate_booking_permission(entity_type_required):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            
            # Check if user type matches required entity type
            if entity_type_required == 'vendor' and current_user.get('user_type') == 'VENUE_PROVIDER':
                return func(*args, **kwargs)
            elif entity_type_required in ['venue', 'vendor'] and current_user.get('user_type') == 'CUSTOMER':
                return func(*args, **kwargs)
            else:
                return jsonify({"message": "Permission denied"}), HttpCodes.HTTP_403_FORBIDDEN
        return wrapper
    return decorator

def validate_hiring_permission(user_type_required):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user = get_jwt_identity()
            if current_user.get('user_type') != user_type_required:
                return jsonify({"message": "Permission denied"}), HttpCodes.HTTP_403_FORBIDDEN
            return func(*args, **kwargs)
        return wrapper
    return decorator