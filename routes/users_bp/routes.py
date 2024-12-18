from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import generate_access_token
from services.email_service import send_verification_email
from services.verification_service import generate_verification_code
from werkzeug.security import generate_password_hash
from .models import *
from routes.bookings_bp.models import Notification
from routes.venue_provider_bp.models import get_user_id_by_email
from utils import HttpCodes
from bson import ObjectId
from routes.staff_bp.models import Staff

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    existing_user = User.find_by_email(data['email'])
    
    if existing_user:
        return jsonify({"message": "User already exists"}), HttpCodes.HTTP_400_BAD_REQUEST
    
    verification_code = generate_verification_code()

    user = User(
        email=data['email'],
        password=data['password'],
        full_name=data['full_name'],
        username=data['username'],
        user_type=data['user_type'],
        verification_code=verification_code
    )
    
    user.save()
    send_verification_email(data['email'], verification_code)

    user_info = {
        "email": user.email,
        "full_name": user.full_name,
        "username": user.username,
        "user_type": user.user_type,
        "is_verified": user.is_verified
    }
    
    return jsonify({
        "message": "User created. Verification email sent.",
        "user": user_info
    }), HttpCodes.HTTP_201_OK

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.find_by_email(data['email'])
    
    if not user or not User.verify_password(user['password'], data['password']):
        return jsonify({"message": "Invalid credentials"}), HttpCodes.HTTP_401_UNAUTHORIZED

    if not user['is_verified']:
        return jsonify({"message": "Email not verified"}), HttpCodes.HTTP_403_NOT_VERIFIED

    token = generate_access_token(user['email'])

    user_info = {
        "email": user['email'],
        "full_name": user['full_name'],
        "username": user['username'],
        "user_type": user['user_type'],
        "is_verified": user['is_verified']
    }

    return jsonify({
        "token": token,
        "user": user_info
    }), HttpCodes.HTTP_200_OK

@users_bp.route('/user/update', methods=['PUT'])
@jwt_required()
def update_user():
    """Update user details for the logged-in user."""
    current_user_email = get_jwt_identity()
    current_user = User.find_by_email(current_user_email['email'])

    if not current_user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    data = request.json
    update_data = {}

    # Update fields if provided in the request
    if 'email' in data:
        update_data['email'] = data['email']
    if 'full_name' in data:
        update_data['full_name'] = data['full_name']
    if 'username' in data:
        update_data['username'] = data['username']

    if not update_data:
        return jsonify({"message": "No data provided for update"}), HttpCodes.HTTP_400_BAD_REQUEST

    # Update the user record in the database
    result = mongo.db['User'].update_one(
        {"_id": ObjectId(current_user['_id'])},
        {"$set": update_data}
    )

    if result.matched_count > 0:
        return jsonify({"message": "User details updated successfully"}), HttpCodes.HTTP_200_OK
    return jsonify({"error": "Failed to update user details"}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@users_bp.route('/verify_password', methods=['POST'])
@jwt_required()
def verify_password():
    data = request.json
    current_user_email = get_jwt_identity()
    user = User.find_by_email(current_user_email['email'])

    if not user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    if not check_password_hash(user['password'], data['password']):
        return jsonify({"message": "Invalid password"}), HttpCodes.HTTP_401_UNAUTHORIZED

    return jsonify({"message": "Password verified successfully"}), HttpCodes.HTTP_200_OK

@users_bp.route('/get_vcode', methods=['POST'])
def get_verification_code():
    data = request.json
    user = User.find_by_email(data['email'])
    
    if not user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    verification_code = generate_verification_code()
    mongo.db['User'].update_one(
            {"email": data['email']},
            {"$set": {"verification_code": verification_code}}
        )
    send_verification_email(data['email'], verification_code, is_signup=False)

    return jsonify({"message": "Verification code sent"}), HttpCodes.HTTP_200_OK

@users_bp.route('/reset_password/verify', methods=['POST'])
def verify_code():
    data = request.json
    verification_code = data.get('verification_code')
    
    if not verification_code:
        return jsonify({"message": "Invalid verification code"}), HttpCodes.HTTP_400_BAD_REQUEST
    
    user = User.find_by_email(data['email'])
    
    if not user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    if user['verification_code'] == verification_code:
        mongo.db['User'].update_one(
            {"email": data['email']},
            {"$set": {"is_verified": True}}
        )
        return jsonify({"message": "Verification successful"}), HttpCodes.HTTP_200_OK
    
    return jsonify({"message": "Invalid verification code"}), HttpCodes.HTTP_400_BAD_REQUEST


@users_bp.route('/reset_password/update', methods=['POST'])
def reset_password():
    data = request.json
    user = User.find_by_email(data['email'])
    
    if not user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    if user['is_verified'] == True:
        new_password_hash = generate_password_hash(data['password'])
        mongo.db['User'].update_one(
            {"email": data['email']},
            {"$set": {"password": new_password_hash}}
        )
        return jsonify({"message": "Password updated successfully"}), HttpCodes.HTTP_200_OK
    
    return jsonify({"message": "Invalid verification code"}), HttpCodes.HTTP_400_BAD_REQUEST

@users_bp.route('/all_users', methods=['GET'])
def get_all_users():
    """
    Get all users along with their details, including unhashed passwords.
    This is for personal reference only and should not be used in production.
    """
    try:
        # Fetch all users from the database
        users = mongo.db['User'].find()
        user_list = [
            {
                "email": user['email'],
                "password": user['password'],  # This is the hashed password stored in the database
                "full_name": user['full_name'],
                "username": user['username'],
                "user_type": user['user_type'],
                "is_verified": user['is_verified']
            }
            for user in users
        ]

        return jsonify({"users": user_list}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@users_bp.route('/user/delete', methods=['DELETE'])
@jwt_required()
def delete_user():
    """
    Delete a user account after verifying the password.

    If the user is of type 'STAFF', also delete associated data from the Staff collection.
    """
    data = request.json
    if 'password' not in data:
        return jsonify({"message": "Password is required"}), HttpCodes.HTTP_400_BAD_REQUEST

    # Get current user's email and find user document
    current_user_email = get_jwt_identity()
    current_user = User.find_by_email(current_user_email)

    if not current_user:
        return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

    # Verify the provided password
    if not check_password_hash(current_user['password'], data['password']):
        return jsonify({"message": "Incorrect password"}), HttpCodes.HTTP_401_UNAUTHORIZED

    # Delete user from the 'User' collection
    user_deletion_result = mongo.db['User'].delete_one({'_id': ObjectId(current_user['_id'])})

    if user_deletion_result.deleted_count == 1:
        # Check if user is of type 'STAFF' and delete related staff data
        if current_user.get('user_type') == 'STAFF':
            staff_deletion_result = Staff.delete_by_id(current_user['_id'])
            if staff_deletion_result.deleted_count == 0:
                return jsonify({"message": "User deleted, but no related staff data found"}), HttpCodes.HTTP_200_OK

        return jsonify({"message": "User and associated staff data deleted successfully"}), HttpCodes.HTTP_200_OK
    else:
        return jsonify({"error": "Failed to delete user"}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@users_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        current_user = get_jwt_identity()
        user_id = get_user_id_by_email(current_user.get('email'))
        is_read = request.args.get('is_read')
        is_read = True if is_read == 'true' else False if is_read == 'false' else None

        notifications = Notification.find_by_user_id(user_id, is_read=is_read)
        if notifications:
            return jsonify({"notifications": notifications}), HttpCodes.HTTP_200_OK
        else:
            return jsonify({"notifications": []}), HttpCodes.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({"message": "Failed to get notification.", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@users_bp.route('/notifications/<notification_id>/read', methods=['PATCH'])
@jwt_required()
def mark_notification_as_read(notification_id):
    try:
        result = Notification.mark_as_read(notification_id)
        if result.modified_count == 0:
            return jsonify({"message": "Notification not found or already marked as read"}), HttpCodes.HTTP_404_NOT_FOUND

        return jsonify({"message": "Notification marked as read"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@users_bp.route('/notifications/read-all', methods=['PATCH'])
@jwt_required()
def mark_all_notifications_as_read():
    user_id = get_jwt_identity()
    try:
        result = mongo.db['Notifications'].update_many(
            {"user_id": ObjectId(user_id), "is_read": False},
            {"$set": {"is_read": True}}
        )
        if result.modified_count == 0:
            return jsonify({"message": "No unread notifications found"}), HttpCodes.HTTP_404_NOT_FOUND

        return jsonify({"message": f"{result.modified_count} notifications marked as read"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR