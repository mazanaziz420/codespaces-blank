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
        booked_dates = [date for booking in bookings for date in booking['booking_date_range']]
        return jsonify({"not_available_dates": booked_dates}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/entities/<entity_type>/<entity_id>/book', methods=['POST'])
def book_entity(entity_type, entity_id):
    """Book a venue or vendor."""
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

        # Notify owner about the booking request
        send_booking_request_notification_to_provider(owner_email, entity_name, customer_email, booking_date_range)
        create_notification_for_booking(owner_id, f"You received a booking request for {entity_name}", booking_id, entity_id, entity_type)

        socketio.emit('booking_request', {
            'message': f"You received a booking request for {entity_name}",
            'entity_id': str(entity_id),
            'customer_email': customer_email
        }, namespace='/notifications')

        return jsonify({"message": "Booking request submitted", "booking_id": str(booking_id)}), HttpCodes.HTTP_201_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/accept', methods=['POST'])
def accept_booking(booking_id):
    """Accept a booking request."""
    try:
        Booking.update_status(booking_id, 'booked')

        # Fetch booking and entity details for notifications
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        customer_id = booking['customer_id']
        entity_id = booking['venue_id'] or booking['vendor_id']
        entity_type = 'venue' if booking['venue_id'] else 'vendor'

        entity_name, _, _ = get_entity_details(entity_id, entity_type)
        customer = mongo.db['User'].find_one({"_id": ObjectId(customer_id)})
        customer_email = customer['email']

        create_notification_for_booking(customer_id, f"Your booking for {entity_name} has been accepted.", booking_id, entity_id, entity_type)
        send_booking_status_notification_to_customer(customer_email, entity_name, 'accepted')

        socketio.emit('booking_status', {
            'message': f"Your booking for {entity_name} has been accepted.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')

        return jsonify({"message": "Booking accepted"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/reject', methods=['POST'])
def reject_booking(booking_id):
    """Reject a booking request."""
    try:
        Booking.update_status(booking_id, 'rejected')

        # Fetch booking and entity details for notifications
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        customer_id = booking['customer_id']
        entity_id = booking['venue_id'] or booking['vendor_id']
        entity_type = 'venue' if booking['venue_id'] else 'vendor'

        entity_name, _, _ = get_entity_details(entity_id, entity_type)
        customer = mongo.db['User'].find_one({"_id": ObjectId(customer_id)})
        customer_email = customer['email']

        create_notification_for_booking(customer_id, f"Your booking for {entity_name} has been rejected.", booking_id, entity_id, entity_type)
        send_booking_status_notification_to_customer(customer_email, entity_name, 'rejected')

        socketio.emit('booking_status', {
            'message': f"Your booking for {entity_name} has been rejected.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')

        return jsonify({"message": "Booking rejected"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/entities/<entity_type>/provider/bookings', methods=['POST'])
def get_bookings_for_provider(entity_type):
    """Get all bookings for a provider based on the entity type."""
    try:
        # Extract provider_id from the request body
        data = request.json
        provider_id = data.get('provider_id')

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
        # Fetch bookings based on the query
        bookings = mongo.db['Bookings'].find(query)
        booking_list = [
            {
                "_id": str(booking["_id"]),
                "customer_id": str(booking["customer_id"]),
                "entity_id": str(booking["venue_id"]) if entity_type == 'venue' else str(booking["vendor_id"]),
                "entity_type": entity_type,
                "booking_date_range": booking["booking_date_range"],
                "status": booking["status"],
                "requested_at": booking["requested_at"].isoformat(),
                "updated_at": booking["updated_at"].isoformat()
            }
            for booking in bookings
        ]

        # Return the list of bookings
        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/admin/bookings', methods=['GET'])
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
