from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import *
from routes.helpers import upload_image
from routes.venue_provider_bp.models import get_user_id_by_email
from .models import Staff
from utils import HttpCodes
from bson import ObjectId

staff_bp = Blueprint('staff_bp', __name__)

@staff_bp.route('/add-data', methods=['POST'])
@jwt_required()
def add_staff_data():
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'STAFF':
        return jsonify({"message": "Permission denied!"}), HttpCodes.HTTP_403_NOT_VERIFIED
    
    user_id = get_user_id_by_email(current_user['email'])
    
    # Ensure the user_id is valid
    if not user_id or len(user_id) != 24:
        return jsonify({"error": "Invalid user ID."}), HttpCodes.HTTP_400_BAD_REQUEST
    """Add new staff data from form-data."""
    try:
        files = request.files
        profile_picture_url = None
        profile_picture_url = upload_image(files['profilePhoto'])
        resume_url = None
        resume_url = upload_image(files['resume'])
        

        # Extract form data
        staff_data = {field: request.form.get(field) for field in Staff().__dict__.keys()}
        # Add user_id to staff data after it's initialized
        staff_data['user_id'] = user_id
        staff_data['profilePhoto'] = profile_picture_url
        staff_data['resume'] = resume_url
        # Convert boolean fields manually
        staff_data['agreement'] = staff_data.get('agreement', 'false').lower() == 'true'
        staff_data['privacyConsent'] = staff_data.get('privacyConsent', 'false').lower() == 'true'
        
        # Initialize Staff object
        staff = Staff(**staff_data)
        result = staff.save()
        
        # Extract the inserted staff_id (usually stored in result.inserted_id)
        staff_id = str(result.inserted_id)

        return jsonify({"message": "Staff data added successfully", "staff-id": staff_id}), HttpCodes.HTTP_201_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@staff_bp.route('/get/<staff_id>', methods=['GET'])
@jwt_required()
def get(staff_id):
    current_user = get_jwt_identity()
    try:
        staff = mongo.db['Staff'].find_one({"_id": ObjectId(staff_id)})
        if not staff:
            return jsonify({"error": "Staff details not found."}), HttpCodes.HTTP_404_NOT_FOUND
        
        user = mongo.db['User'].find_one({"_id": ObjectId(staff['user_id'])})
        if not user:
            return jsonify({"error": "User not found."}), HttpCodes.HTTP_404_NOT_FOUND
        
        # Prepare the response with user and staff details in one dictionary under "staff_details"
        response_data = {
            "staff_details": {
                "email": user['email'],
                "full_name": user['full_name'],
                "username": user['username'],
                "phoneNumber": staff['phoneNumber'],
                "dateOfBirth": staff['dateOfBirth'],
                "gender": staff['gender'],
                "city": staff['city'],
                "state": staff['state'],
                "idCardNumber": staff['idCardNumber'],
                "experienceYears": staff['experienceYears'],
                "previousEmployers": staff['previousEmployers'],
                "relevantSkills": staff['relevantSkills'],
                "daysAvailable": staff['daysAvailable'],
                "preferredShifts": staff['preferredShifts'],
                "noticePeriod": staff['noticePeriod'],
                "currentAddress": staff['currentAddress'],
                "preferredWorkLocations": staff['preferredWorkLocations'],
                "foodCertifications": staff['foodCertifications'],
                "tipsCertification": staff['tipsCertification'],
                "firstAidTraining": staff['firstAidTraining'],
                "eventTypes": staff['eventTypes'],
                "rolesPerformed": staff['rolesPerformed'],
                "profilePhoto": staff['profilePhoto'],
                "resume": staff['resume'],
                "references": staff['references'],
                "hourlyRate": staff['hourlyRate'],
                "specialSkills": staff['specialSkills'],
                "specialRequirements": staff['specialRequirements'],
                "additionalComments": staff['additionalComments'],
                "agreement": staff['agreement'],
                "privacyConsent": staff['privacyConsent']
            }
        }
        
        return jsonify(response_data), HttpCodes.HTTP_200_OK
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@staff_bp.route('/get-all-staff-members-details', methods=['GET'])
def get_all_staff_data():
    try:
        staffs = Staff.find_all()
        if staffs:
            for staff in staffs:
                user_id = staff['user_id']
                user = mongo.db['User'].find_one({"_id": ObjectId(user_id)})
                staff['username'] = user['username']
                staff['full_name'] = user['full_name']
                staff['email'] = user['email']
                staff['user_id'] = str(user_id)

            return jsonify(staffs), HttpCodes.HTTP_200_OK
        else:
            return jsonify({"message": "No data found!"}), HttpCodes.HTTP_400_BAD_REQUEST

    except Exception as e:
        return jsonify({"message": "Error in Fetching Staff", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@staff_bp.route('/edit-data/<staff_id>', methods=['PUT'])
@jwt_required()
def edit_staff_data(staff_id):
    """Edit existing staff data by ID."""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'STAFF':
        return jsonify({"message": "Permission denied!"}), HttpCodes.HTTP_403_NOT_VERIFIED
    try:
        # Extract form data for updating
        update_data = {field: request.form.get(field) for field in Staff().__dict__.keys()}
        
        # Convert boolean fields manually
        update_data['agreement'] = update_data.get('agreement', 'false').lower() == 'true'
        update_data['privacyConsent'] = update_data.get('privacyConsent', 'false').lower() == 'true'

        # Remove fields with None values to avoid overwriting existing data unnecessarily
        update_data = {k: v for k, v in update_data.items() if v is not None}

        # Update the staff member in the database
        result = Staff.update_by_id(staff_id, update_data)

        if result.modified_count > 0:
            return jsonify({"message": "Staff data updated successfully"}), HttpCodes.HTTP_200_OK
        else:
            return jsonify({"message": "No updates made"}), HttpCodes.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@staff_bp.route('/delete-data/<staff_id>', methods=['DELETE'])
@jwt_required()
def delete_staff_data(staff_id):
    """Delete a staff record by ID."""
    current_user = get_jwt_identity()
    if current_user['user_type'] != 'STAFF':
        return jsonify({"message": "Permission denied!"}), HttpCodes.HTTP_403_NOT_VERIFIED
    try:
        result = Staff.delete_by_id(staff_id)
        if result.deleted_count > 0:
            return jsonify({"message": "Staff data deleted successfully"}), HttpCodes.HTTP_200_OK
        else:
            return jsonify({"message": "Staff data not found"}), HttpCodes.HTTP_404_NOT_FOUND
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR