from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from routes.venue_provider_bp.models import get_user_id_by_email
from utils import HttpCodes
from .models import Booking, Notification
from models import mongo
from bson import ObjectId
from services.email_service import send_booking_status_notification_to_customer, send_booking_request_notification_to_provider
from routes.users_bp.models import User
from socketio_instance import socketio
from decorator import validate_booking_permission

bookings_bp = Blueprint('bookings_bp', __name__)

def get_entity_details(entity_id, entity_type):
    """Fetch details of either a venue or vendor based on the entity type."""
    
    if entity_type == 'venue':
        entity = mongo.db['VenueProvider'].find_one({"_id": ObjectId(entity_id)})
        if entity:
            entity_name = entity['name_of_venue']
            entity_owner = mongo.db['User'].find_one({"_id": ObjectId(entity['created_by'])})
    elif entity_type == 'vendor':
        entity = mongo.db['Vendors'].find_one({"_id": ObjectId(entity_id)})
        if entity:
            entity_name = entity['name']
            entity_owner = mongo.db['User'].find_one({"_id": ObjectId(entity['created_by'])})
    else:
        return None, None, None

    if entity and entity_owner:
        owner_email = entity_owner['email']
        owner_id = entity_owner['_id']
        return entity_name, owner_email, owner_id
    return None, None, None

def create_notification_for_booking(user_id, message, booking_id, entity_id, entity_type):
    """Create a notification for a booking."""
    notification = Notification(
        user_id=user_id,
        message=message,
        booking_id=booking_id,
        venue_id=entity_id if entity_type == 'venue' else None,
        vendor_id=entity_id if entity_type == 'vendor' else None
    )
    notification.save()

@bookings_bp.route('/entities/<entity_type>/<entity_id>/availability', methods=['GET'])
def check_availability(entity_type, entity_id):
    """Check availability for venue or vendor."""
    try:
        bookings = Booking.find_by_entity(entity_id, entity_type)
        # Extract and flatten all booked dates from each booking
        booked_dates = [date for booking in bookings for date in booking['booking_date_range']]
        # Remove duplicates by converting to a set, then back to a list
        unique_booked_dates = list(set(booked_dates))
        # Sort the dates for a consistent response (optional)
        unique_booked_dates.sort()
        entity_name, owner_email, owner_id = get_entity_details(entity_id, entity_type)
        return jsonify({
            "booked_dates": unique_booked_dates, 
            "entity_name": entity_name, 
            "owner_email": owner_email
        }), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/entities/<entity_type>/<entity_id>/book', methods=['POST'])
@jwt_required()
@validate_booking_permission(entity_type_required='vendor')
def book_entity(entity_type, entity_id):
    """Book a venue or vendor and return detailed booking information."""
    try:
        data = request.json
        customer_email = data['customer_email']
        customer_id = get_user_id_by_email(customer_email)

        if not customer_id:
            return jsonify({"message": "Customer not found"}), HttpCodes.HTTP_404_NOT_FOUND

        booking_date_range = data['booking_date_range']

        # Check if the requested dates are already booked
        bookings = Booking.find_by_entity(entity_id, entity_type)
        booked_dates = [date for booking in bookings for date in booking['booking_date_range']]
        if any(date in booked_dates for date in booking_date_range):
            return jsonify({"error": "Some or all dates are already booked"}), HttpCodes.HTTP_400_BAD_REQUEST

        # Get entity details (venue or vendor)
        entity_name, owner_email, owner_id = get_entity_details(entity_id, entity_type)
        if not entity_name or not owner_email or not owner_id:
            return jsonify({"message": "Entity not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Save new booking
        new_booking = Booking(
            customer_id=customer_id,
            booking_date_range=booking_date_range,
            venue_id=entity_id if entity_type == 'venue' else None,
            venue_provider_id=owner_id if entity_type == 'venue' else None,
            vendor_id=entity_id if entity_type == 'vendor' else None,
            vendor_provider_id=owner_id if entity_type == 'vendor' else None
        )
        booking_id = new_booking.save()

        # Retrieve detailed information for booking response
        booking_details = {
            "booking_date_range": booking_date_range
        }

        # Get details for venue and vendor based on the type of booking
        if entity_type == 'venue':
            venue_details = mongo.db['VenueProvider'].find_one({"_id": ObjectId(entity_id)})
            venue_provider_details = mongo.db['User'].find_one({"_id": ObjectId(owner_id)})

            booking_details.update({
                "venue_details": {
                    "name": venue_details['name_of_venue'],
                    "city": venue_details['city'],
                    "address": venue_details['address'],
                    "state": venue_details['state'],
                    "capacity": venue_details['capacity'],
                    "size": venue_details['size'],
                    "description": venue_details['place_description'],
                },
                "venue_provider_details": {
                    "full_name": venue_provider_details['full_name'],
                    "email": venue_provider_details['email']
                }
            })

        elif entity_type == 'vendor':
            vendor_details = mongo.db['Vendors'].find_one({"_id": ObjectId(entity_id)})
            vendor_provider_details = mongo.db['User'].find_one({"_id": ObjectId(owner_id)})

            booking_details.update({
                "vendor_details": {
                    "name": vendor_details['name'],
                    "city": vendor_details['city'],
                    "address": vendor_details['address'],
                    "state": vendor_details['state'],
                    "description": vendor_details['description'],
                    "door_to_door_service": vendor_details['door_to_door_service'],
                },
                "vendor_provider_details": {
                    "full_name": vendor_provider_details['full_name'],
                    "email": vendor_provider_details['email']
                }
            })

        # Notify owner about the booking request
        send_booking_request_notification_to_provider(owner_email, entity_name, customer_email, booking_date_range)
        create_notification_for_booking(owner_id, f"You received a booking request for {entity_name}", booking_id, entity_id, entity_type)

        socketio.emit('booking_request', {
            'message': f"You received a booking request for {entity_name}",
            'entity_id': str(entity_id),
            'customer_email': customer_email
        }, namespace='/notifications')

        # Include booking details in the response
        return jsonify({
            "message": "Booking request submitted",
            "booking_id": str(booking_id),
            "booking_details": booking_details
        }), HttpCodes.HTTP_201_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/accept', methods=['POST'])
@jwt_required()
def accept_booking(booking_id):
    """Accept a booking request if user has permission based on entity type."""
    try:
        # Get the current user's type
        current_user = get_jwt_identity()
        user_type = current_user.get('user_type')

        # Fetch booking details
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({"message": "Booking not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Determine entity type and check permissions
        entity_id = booking['venue_id'] or booking['vendor_id']
        entity_type = 'venue' if booking['venue_id'] else 'vendor'

        if (entity_type == 'venue' and user_type != 'VENUE_PROVIDER') or \
           (entity_type == 'vendor' and user_type != 'VENDOR_PROVIDER'):
            return jsonify({"message": "Permission denied"}), HttpCodes.HTTP_403_NOT_VERIFIED

        # Update booking status
        Booking.update_status(booking_id, 'booked')

        # Fetch customer details for notification
        customer_id = booking['customer_id']
        entity_name, _, _ = get_entity_details(entity_id, entity_type)
        customer = mongo.db['User'].find_one({"_id": ObjectId(customer_id)})
        customer_email = customer['email']

        # Send notifications
        create_notification_for_booking(
            customer_id, 
            f"Your booking for {entity_name} has been accepted.", 
            booking_id, 
            entity_id, 
            entity_type
        )
        send_booking_status_notification_to_customer(customer_email, entity_name, 'accepted')
        
        socketio.emit('booking_status', {
            'message': f"Your booking for {entity_name} has been accepted.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')

        return jsonify({"message": "Booking accepted"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/reject', methods=['POST'])
@jwt_required()
def reject_booking(booking_id):
    """Reject a booking request if user has permission based on entity type."""
    try:
        # Get the current user's type
        current_user = get_jwt_identity()
        user_type = current_user.get('user_type')

        # Fetch booking details
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        if not booking:
            return jsonify({"message": "Booking not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Determine entity type and check permissions
        entity_id = booking['venue_id'] or booking['vendor_id']
        entity_type = 'venue' if booking['venue_id'] else 'vendor'

        if (entity_type == 'venue' and user_type != 'VENUE_PROVIDER') or \
           (entity_type == 'vendor' and user_type != 'VENDOR_PROVIDER'):
            return jsonify({"message": "Permission denied"}), HttpCodes.HTTP_403_NOT_VERIFIED

        # Update booking status
        Booking.update_status(booking_id, 'rejected')

        # Fetch customer details for notification
        customer_id = booking['customer_id']
        entity_name, _, _ = get_entity_details(entity_id, entity_type)
        customer = mongo.db['User'].find_one({"_id": ObjectId(customer_id)})
        customer_email = customer['email']

        # Send notifications
        create_notification_for_booking(
            customer_id, 
            f"Your booking for {entity_name} has been rejected.", 
            booking_id, 
            entity_id, 
            entity_type
        )
        send_booking_status_notification_to_customer(customer_email, entity_name, 'rejected')
        
        socketio.emit('booking_status', {
            'message': f"Your booking for {entity_name} has been rejected.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')

        return jsonify({"message": "Booking rejected"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@bookings_bp.route('/entities/<entity_type>/provider/bookings', methods=['GET'])
@jwt_required()
def get_bookings_for_provider(entity_type):
    """Get all bookings for a provider based on the entity type with detailed booking information."""
    try:
        current_user = get_jwt_identity()
        print(current_user)
        provider_id = get_user_id_by_email(current_user.get('email'))
        print(provider_id)
        if not provider_id:
            return jsonify({"message": "Provider ID is required"}), HttpCodes.HTTP_400_BAD_REQUEST

        # Build the query based on entity type
        query = {}
        if entity_type == 'venue':
            query['venue_provider_id'] = ObjectId(provider_id) 
        elif entity_type == 'vendor':
            query['vendor_provider_id'] = ObjectId(provider_id)
        else:
            return jsonify({"message": "Invalid entity type. Must be 'venue' or 'vendor'."}), HttpCodes.HTTP_400_BAD_REQUEST
        print(entity_type)
        print(query)
        # Fetch bookings based on the query
        bookings = mongo.db['Bookings'].find(query)
        booking_list = []

        for booking in bookings:
            # Base booking details
            booking_details = {
                "_id": str(booking["_id"]),
                "customer_id": str(booking["customer_id"]),
                "booking_date_range": booking["booking_date_range"],
                "status": booking["status"],
                "paymentStatus": booking.get("paymentStatus"),
                "requested_at": booking["requested_at"].isoformat(),
                "updated_at": booking["updated_at"].isoformat(),
            }

            # Entity-specific details
            if entity_type == 'venue':
                # Get venue details
                venue_details = mongo.db['VenueProvider'].find_one({"_id": booking["venue_id"]})
                venue_provider_details = mongo.db['User'].find_one({"_id": booking["venue_provider_id"]})
                
                booking_details["venue_details"] = {
                    "name": venue_details['name_of_venue'],
                    "city": venue_details['city'],
                    "address": venue_details['address'],
                    "state": venue_details['state'],
                    "capacity": venue_details['capacity'],
                    "size": venue_details['size'],
                    "description": venue_details['place_description']
                } if venue_details else {}

                booking_details["venue_provider_details"] = {
                    "full_name": venue_provider_details['full_name'],
                    "email": venue_provider_details['email']
                } if venue_provider_details else {}

            elif entity_type == 'vendor':
                # Get vendor details
                vendor_details = mongo.db['Vendors'].find_one({"_id": booking["vendor_id"]})
                vendor_provider_details = mongo.db['User'].find_one({"_id": booking["vendor_provider_id"]})
                
                booking_details["vendor_details"] = {
                    "name": vendor_details['name'],
                    "city": vendor_details['city'],
                    "address": vendor_details['address'],
                    "state": vendor_details['state'],
                    "description": vendor_details['description'],
                    "door_to_door_service": vendor_details['door_to_door_service']
                } if vendor_details else {}

                booking_details["vendor_provider_details"] = {
                    "full_name": vendor_provider_details['full_name'],
                    "email": vendor_provider_details['email']
                } if vendor_provider_details else {}
                
            customer_details = mongo.db['User'].find_one({"_id": ObjectId(booking["customer_id"])})
            customer_email = customer_details['email']
            customer_name = customer_details['full_name']
            customer_type = customer_details['user_type']
            booking_details["customer_details"] = {
                "full_name": customer_name,
                "email": customer_email,
                "user_type": customer_type
            }

            booking_list.append(booking_details)

        # Return the list of bookings with detailed information
        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/admin/bookings', methods=['GET'])
@jwt_required()
def get_all_bookings():
    """Retrieve all bookings."""
    try:
        bookings = mongo.db['Bookings'].find()
        booking_list = [
            {
                "_id": str(booking["_id"]),
                "customer_name": mongo.db['User'].find_one({"_id": booking["customer_id"]})["full_name"],
                "entity_name": mongo.db['VenueProvider'].find_one({"_id": booking["venue_id"]})["name_of_venue"]
                if booking["venue_id"] else mongo.db['Vendors'].find_one({"_id": booking["vendor_id"]})["name"],
                "booking_date_range": booking["booking_date_range"],
                "status": booking["status"]
            }
            for booking in bookings
        ]
        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/customer-bookings', methods=['GET'])
@jwt_required()
def get_bookings_for_customer():
    """Retrieve all bookings made by the logged-in customer."""
    try:
        # Get the current logged-in user's information
        current_user = get_jwt_identity()
        
        # Verify that the user type is "CUSTOMER"
        if current_user.get('user_type') != 'CUSTOMER':
            return jsonify({"message": "Permission denied"}), HttpCodes.HTTP_403_NOT_VERIFIED
        
        # Retrieve the customer's ID and email
        customer_id = get_user_id_by_email(current_user.get('email'))
        if not customer_id:
            return jsonify({"message": "Customer not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Find all bookings associated with this customer
        bookings = mongo.db['Bookings'].find({"customer_id": ObjectId(customer_id)})

        booking_list = []
        
        for booking in bookings:
            # Base booking details
            booking_details = {
                "_id": str(booking["_id"]),
                "booking_date_range": booking["booking_date_range"],
                "status": booking["status"],
                "paymentStatus": booking.get("paymentStatus"),
                "requested_at": booking["requested_at"].isoformat(),
                "updated_at": booking["updated_at"].isoformat(),
                "customer_details": {
                    "full_name": current_user.get('full_name'),
                    "email": current_user.get('email'),
                    "user_type": current_user.get('user_type')
                },
                "customer_id": str(booking["customer_id"]),
            }
            venue_id = booking.get("venue_id")
            # Fetch venue details if the booking is for a venue
            if venue_id:
                venue_details = mongo.db['VenueProvider'].find_one({"_id": venue_id})
                venue_provider_details = mongo.db['User'].find_one({"_id": venue_details["created_by"]})
                
                booking_details["venue_details"] = {
                    "name": venue_details['name_of_venue'],
                    "city": venue_details['city'],
                    "address": venue_details['address'],
                    "state": venue_details['state'],
                    "capacity": venue_details['capacity'],
                    "size": venue_details['size'],
                    "description": venue_details['place_description']
                } if venue_details else {}

                booking_details["venue_provider_details"] = {
                    "full_name": venue_provider_details['full_name'],
                    "email": venue_provider_details['email']
                } if venue_provider_details else {}

            # Fetch vendor details if the booking is for a vendor
            elif booking.get("vendor_id"):
                vendor_details = mongo.db['Vendors'].find_one({"_id": booking["vendor_id"]})
                vendor_provider_details = mongo.db['User'].find_one({"_id": vendor_details['created_by']})

                booking_details["vendor_details"] = {
                    "name": vendor_details['name'],
                    "city": vendor_details['city'],
                    "address": vendor_details['address'],
                    "state": vendor_details['state'],
                    "description": vendor_details['description'],
                    "door_to_door_service": vendor_details['door_to_door_service']
                } if vendor_details else {}

                booking_details["vendor_provider_details"] = {
                    "full_name": vendor_provider_details['full_name'],
                    "email": vendor_provider_details['email']
                } if vendor_provider_details else {}

            booking_list.append(booking_details)

        # Return the list of bookings with detailed information
        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR