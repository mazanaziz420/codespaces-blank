from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import HireRequest
from models import mongo
from decorator import validate_hiring_permission
from services.email_service import send_hire_notification, send_hire_status_notification
from routes.staff_bp.models import Staff
from routes.users_bp.models import User
from routes.venue_provider_bp.models import get_user_id_by_email
from utils import HttpCodes
from bson import ObjectId
from datetime import datetime, timedelta

hiring_staff_bp = Blueprint('hiring_staff_bp', __name__)

def generate_date_range(start_date, end_date):
    """Generate a list of dates between start_date and end_date inclusive."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((end - start).days + 1)]

def check_staff_availability(staff_id, requested_dates):
    """Check if the staff is already booked on any of the requested dates."""
    existing_requests = HireRequest.find_by_staff_id(staff_id)
    booked_dates = set()
    for request in existing_requests:
        booked_dates.update(request['requested_dates'])
    return any(date in booked_dates for date in requested_dates)

@hiring_staff_bp.route('/customer/hire/<staff_id>', methods=['POST'])
@jwt_required()
@validate_hiring_permission(user_type_required='CUSTOMER')
def customer_hire_staff(staff_id):
    current_user = get_jwt_identity()
    hirer_email = current_user["email"]
    user_id = get_user_id_by_email(hirer_email)
    user = mongo.db['User'].find_one({"_id": ObjectId(user_id)})
    hirer_name = user.get('full_name')
    hirer_type = user.get('user_type')
    
    # Get date range from request
    request_date_from = request.json.get('request_date_from')
    request_date_to = request.json.get('request_date_to')
    if not request_date_from or not request_date_to:
        return jsonify({"error": "Please provide both 'request_date_from' and 'request_date_to'"}), HttpCodes.HTTP_400_BAD_REQUEST

    # Generate list of requested dates
    requested_dates = generate_date_range(request_date_from, request_date_to)

    # Check if staff is available for all requested dates
    if check_staff_availability(staff_id, requested_dates):
        return jsonify({"error": "The staff is already booked on one or more of the requested dates."}), HttpCodes.HTTP_400_BAD_REQUEST

    # Extract additional data from request
    message = request.json.get('message')
    time = request.json.get('time')
    wageOffered = request.json.get('wageOffered')
    city = request.json.get('city')
    venueLocation = request.json.get('venueLocation')
    eventType = request.json.get('eventType')
    numberOfGuests = request.json.get('numberOfGuests')

    try:
        # Save the hire request
        hire_request = HireRequest(
            staff_id=staff_id,
            hirer_id=user_id,
            hirer_type=hirer_type,
            requested_dates=requested_dates,
            message=message,
            time=time,
            wageOffered=wageOffered,
            city=city,
            venueLocation=venueLocation,
            eventType=eventType,
            numberOfGuests=numberOfGuests
        )
        hire_request_id = hire_request.save()

        # Fetch staff details
        staff = mongo.db['Staff'].find_one({"_id": ObjectId(staff_id)})
        staff_details = mongo.db['User'].find_one({"_id": staff['user_id']})
        staff_email = staff_details["email"]

        # Send email notification to staff
        send_hire_notification(staff_email, hirer_name, "Customer", requested_dates)

        # Return detailed response
        return jsonify({
            "message": "Hire request submitted successfully", 
            "hire_request_id": str(hire_request_id),
            "requested_dates": requested_dates,
            "hirer_details": {
                "name": hirer_name,
                "email": hirer_email,
                "type": hirer_type
            },
            "staff_details": {
                "name": staff_details.get("full_name"),
                "email": staff_email
            }
        }), HttpCodes.HTTP_201_OK
    
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

# Venue provider hire route, similar to customer_hire_staff with minor modifications
@hiring_staff_bp.route('/venue_provider/hire/<staff_id>', methods=['POST'])
@jwt_required()
@validate_hiring_permission(user_type_required='VENUE_PROVIDER')
def venue_provider_hire_staff(staff_id):
    current_user = get_jwt_identity()
    hirer_email = current_user["email"]
    user_id = get_user_id_by_email(hirer_email)
    user = mongo.db['User'].find_one({"_id": ObjectId(user_id)})
    hirer_name = user.get('full_name')
    hirer_type = user.get('user_type')
    
    # Get date range from request
    request_date_from = request.json.get('request_date_from')
    request_date_to = request.json.get('request_date_to')
    if not request_date_from or not request_date_to:
        return jsonify({"error": "Please provide both 'request_date_from' and 'request_date_to'"}), HttpCodes.HTTP_400_BAD_REQUEST

    # Generate list of requested dates
    requested_dates = generate_date_range(request_date_from, request_date_to)

    # Check if staff is available for all requested dates
    if check_staff_availability(staff_id, requested_dates):
        return jsonify({"error": "The staff is already booked on one or more of the requested dates."}), HttpCodes.HTTP_400_BAD_REQUEST

    # Extract additional data from request
    message = request.json.get('message')
    time = request.json.get('time')
    wageOffered = request.json.get('wageOffered')
    city = request.json.get('city')
    venueLocation = request.json.get('venueLocation')
    eventType = request.json.get('eventType')
    numberOfGuests = request.json.get('numberOfGuests')

    try:
        # Save the hire request
        hire_request = HireRequest(
            staff_id=staff_id,
            hirer_id=user_id,
            hirer_type=hirer_type,
            requested_dates=requested_dates,
            message=message,
            time=time,
            wageOffered=wageOffered,
            city=city,
            venueLocation=venueLocation,
            eventType=eventType,
            numberOfGuests=numberOfGuests
        )
        hire_request_id = hire_request.save()

        # Fetch staff details
        staff = mongo.db['Staff'].find_one({"_id": ObjectId(staff_id)})
        staff_details = mongo.db['User'].find_one({"_id": staff['user_id']})
        staff_email = staff_details["email"]

        # Send email notification to staff
        send_hire_notification(staff_email, hirer_name, "Venue Provider", requested_dates)

        # Return detailed response
        return jsonify({
            "message": "Hire request submitted successfully", 
            "hire_request_id": str(hire_request_id),
            "requested_dates": requested_dates,
            "hirer_details": {
                "name": hirer_name,
                "email": hirer_email,
                "type": hirer_type
            },
            "staff_details": {
                "name": staff_details.get("full_name"),
                "email": staff_email
            }
        }), HttpCodes.HTTP_201_OK
    
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@hiring_staff_bp.route('/staff/<staff_id>/availability', methods=['GET'])
def check_staff_availability_api(staff_id):
    """Public API to check the availability of staff, returns list of booked dates."""
    existing_requests = HireRequest.find_by_staff_id(staff_id)
    booked_dates = set()
    for request in existing_requests:
        booked_dates.update(request['requested_dates'])
    
    return jsonify({"booked_dates": list(booked_dates)}), HttpCodes.HTTP_200_OK

@hiring_staff_bp.route('/hire_request/<hire_request_id>/accept', methods=['GET'])
@jwt_required()
@validate_hiring_permission(user_type_required='STAFF')
def accept_hire_request(hire_request_id):
    """Staff can accept a hire request."""
    try:
        # Retrieve the hire request details
        hire_request = mongo.db['HireRequests'].find_one({"_id": ObjectId(hire_request_id)})

        # Check if the hire request was found
        if not hire_request:
            return jsonify({"error": "Hire request not found"}), HttpCodes.HTTP_404_NOT_FOUND
        
        if hire_request['status'] != "pending":
            return jsonify({"message": "Invalid Request!"}), HttpCodes.HTTP_400_BAD_REQUEST

        # Update the status of the hire request
        HireRequest.update_status(hire_request_id, "accepted")
        
        # Get the current staff member's email and ID
        staff_email = get_jwt_identity().get("email")
        staff_id = get_user_id_by_email(staff_email)
        staff_details = mongo.db['User'].find_one({"_id": ObjectId(staff_id)})
        
        # Check if staff details were found
        if not staff_details:
            return jsonify({"error": "Staff details not found"}), HttpCodes.HTTP_404_NOT_FOUND
        
        staff_name = staff_details.get('full_name')
        
        hirer_id = hire_request.get("hirer_id")
        
        # Retrieve hirer details using the hirer ID from the hire request
        hirer_details = mongo.db['User'].find_one({"_id": ObjectId(hirer_id)})
        
        # Check if hirer details were found
        if not hirer_details:
            return jsonify({"error": "Hirer details not found"}), HttpCodes.HTTP_404_NOT_FOUND
        
        hirer_email = hirer_details.get("email")
        hirer_name = hirer_details.get('full_name')
        
        # Send notification to hirer
        send_hire_status_notification(hirer_email, staff_name, "accepted", hire_request.get("requested_dates"))

        return jsonify({"message": "Hire request accepted"}), HttpCodes.HTTP_200_OK
    
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@hiring_staff_bp.route('/hire_request/<hire_request_id>/reject', methods=['GET'])
@jwt_required()
@validate_hiring_permission(user_type_required='STAFF')
def reject_hire_request(hire_request_id):
    """Staff can reject a hire request."""
    try:
        # Retrieve the hire request details
        hire_request = mongo.db['HireRequests'].find_one({"_id": ObjectId(hire_request_id)})

        # Check if the hire request was found
        if not hire_request:
            return jsonify({"error": "Hire request not found"}), HttpCodes.HTTP_404_NOT_FOUND
        
        if hire_request['status'] != "pending":
            return jsonify({"message": "Invalid Request!"}), HttpCodes.HTTP_400_BAD_REQUEST
        
        HireRequest.update_status(hire_request_id, "rejected")

        # Fetch hire request details
        staff_email = get_jwt_identity().get("email")
        staff_id = get_user_id_by_email(staff_email)
        staff_details = mongo.db['User'].find_one({"_id": ObjectId(staff_id)})
        staff_name = staff_details.get('full_name')

        hirer_id = hire_request["hirer_id"]
        hirer_details = mongo.db['User'].find_one({"_id": ObjectId(hirer_id)})
        hirer_email = hirer_details["email"]
        hirer_name = hirer_details.get('full_name') 

        # Send notification to hirer
        send_hire_status_notification(hirer_email, staff_name, "rejected", hire_request["requested_dates"])

        return jsonify({"message": "Hire request rejected"}), HttpCodes.HTTP_200_OK
    
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@hiring_staff_bp.route('/hire_requests', methods=['GET'])
@jwt_required()
def get_hire_requests_by_event_type():
    current_user = get_jwt_identity()
    hirer_id = get_user_id_by_email(current_user["email"])

    try:
        # Filter hire requests by hirer_id and eventType
        hire_requests = list(mongo.db['HireRequests'].find({
            "hirer_id": ObjectId(hirer_id)
        }))
        
        # Prepare the response
        result = []
        for request in hire_requests:
            staff = mongo.db['Staff'].find_one({"_id": request["staff_id"]})
            staff_details = mongo.db['User'].find_one({"_id": staff["user_id"]})
            
            request_data = {
                "hire_request_id": str(request["_id"]),
                "requested_dates": request["requested_dates"],
                "message": request["message"],
                "time": request["time"],
                "wageOffered": request["wageOffered"],
                "city": request["city"],
                "venueLocation": request["venueLocation"],
                "eventType": request["eventType"],
                "numberOfGuests": request["numberOfGuests"],
                "status": request["status"],
                "staff_details": {
                    "name": staff_details.get("full_name"),
                    "email": staff_details.get("email"),
                }
            }
            result.append(request_data)

        return jsonify(result), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR