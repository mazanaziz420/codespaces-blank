from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils import HttpCodes
from .models import Booking, Notification
from models import mongo
from bson import ObjectId
from services.email_service import send_booking_status_notification_to_customer, send_booking_request_notification_to_provider
from routes.venue_provider_bp.models import VenueProvider, get_user_id_by_email
from routes.users_bp.models import User
from socketio_instance import socketio

bookings_bp = Blueprint('bookings_bp', __name__)

@bookings_bp.route('/venues/<venue_id>/availability', methods=['GET'])
def check_availability(venue_id):
    try:
        bookings = Booking.find_by_venue_id(venue_id)
        booked_dates = [date for booking in bookings for date in booking['booking_date_range']]
        return jsonify({"not_available_dates": booked_dates}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/provider/bookings', methods=['POST'])
def get_bookings_for_provider():
    """
    Get bookings for the venues owned by the logged-in venue provider.
    Accepts an optional query parameter 'status' to filter by booking status.
    """
    try:
        # Assuming the provider ID is provided as a query parameter or from an authenticated session
        provider_id = request.json.get('provider_id')
        status = request.json.get('status')  # Optional filter for booking status

        # Fetch venues owned by the provider
        venues = mongo.db['VenueProvider'].find({"created_by": provider_id})
        venue_ids = [venue['_id'] for venue in venues]

        # Build the query to fetch bookings for the provider's venues
        query = {"venue_id": {"$in": venue_ids}}
        print('query: ', query)
        if status:
            query["status"] = status

        # Get the bookings
        bookings = mongo.db['Bookings'].find(query)
        booking_list = [
            {
                **booking,
                '_id': str(booking['_id']),
                'customer_id': str(booking['customer_id']),
                'venue_id': str(booking['venue_id']),
                'requested_at': booking['requested_at'].isoformat(),
                'updated_at': booking['updated_at'].isoformat(),
            } for booking in bookings
        ]

        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/venues/<venue_id>/book', methods=['POST'])
def book_venue(venue_id):
    try:
        data = request.json
        customer_email = data['customer_email']
        customer_id = get_user_id_by_email(customer_email)
    
        if not customer_id:
            return jsonify({"message": "Costumer not found"}), HttpCodes.HTTP_404_NOT_FOUND
        
        booking_date_range = data['booking_date_range']

        # Check if the requested dates are already booked
        bookings = Booking.find_by_venue_id(venue_id)
        booked_dates = [date for booking in bookings for date in booking['booking_date_range']]
        if any(date in booked_dates for date in booking_date_range):
            return jsonify({"error": "Some or all dates are already booked"}), HttpCodes.HTTP_400_BAD_REQUEST

        # Save new booking
        new_booking = Booking(customer_id, venue_id, booking_date_range)
        booking_id = new_booking.save()

        # Fetch venue details to get provider's email
        venue = mongo.db['VenueProvider'].find_one({"_id": ObjectId(venue_id)})
        provider_email = venue['email']
        venue_name = venue['name_of_venue']
        venue_provider_id = venue['created_by']
        # Fetch customer details for notification
        customer = User.find_by_email(data['customer_email'])
        customer_name = customer['full_name']

        # Notify venue provider about the booking request
        send_booking_request_notification_to_provider(provider_email, venue_name, customer_name, booking_date_range)
        
        notification = Notification(
            user_id=venue_provider_id,
            message=f"You received a booking request from {customer_name} for {venue_name}",
            venue_id=venue_id,
            booking_id=booking_id
        )
        notification.save()
        
        socketio.emit('booking_request', {
            'message': f"You received a booking request from {customer_name} for {venue_name}",
            'venue_id': str(venue_id),
            'customer_name': customer_name
        }, namespace='/notifications')
        return jsonify({"message": "Booking request submitted", "booking_id": str(booking_id)}), HttpCodes.HTTP_201_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/accept', methods=['POST'])
def accept_booking(booking_id):
    try:
        # Update booking status
        Booking.update_status(booking_id, 'booked')

        # Fetch booking and venue details for notifications
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        customer_id = booking['customer_id']
        venue_id = booking['venue_id']

        venue = mongo.db['VenueProvider'].find_one({"_id": venue_id})
        venue_name = venue['name_of_venue']

        customer = mongo.db['User'].find_one({"_id": customer_id})
        customer_email = customer['email']

        notification = Notification(
            user_id=customer_id,
            message=f"Your booking request for {venue_name} has been accepted.",
            booking_id=booking_id,
            venue_id=venue_id
            
        )
        notification.save()
        
        # Notify the customer about the booking acceptance
        send_booking_status_notification_to_customer(customer_email, venue_name, 'accepted')
        
        socketio.emit('booking_status', {
            'message': f"Your booking request for {venue_name} has been accepted.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')

        return jsonify({"message": "Booking accepted"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@bookings_bp.route('/<booking_id>/reject', methods=['POST'])
def reject_booking(booking_id):
    try:
        # Update booking status
        Booking.update_status(booking_id, 'rejected')

        # Fetch booking and venue details for notifications
        booking = mongo.db['Bookings'].find_one({"_id": ObjectId(booking_id)})
        customer_id = booking['customer_id']
        venue_id = booking['venue_id']

        venue = mongo.db['VenueProvider'].find_one({"_id": venue_id})
        venue_name = venue['name_of_venue']

        customer = mongo.db['User'].find_one({"_id": customer_id})
        customer_email = customer['email']

        notification = Notification(
            user_id=customer_id,
            message=f"Your booking request for {venue_name} has been rejected.",
            booking_id=booking_id,
            venue_id=venue_id
        )
        notification.save()
        
        # Notify the customer about the booking rejection
        send_booking_status_notification_to_customer(customer_email, venue_name, 'rejected')
        
        socketio.emit('booking_status', {
            'message': f"Your booking request for {venue_name} has been rejected.",
            'booking_id': str(booking_id)
        }, namespace='/notifications')
        
        return jsonify({"message": "Booking rejected"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@bookings_bp.route('/admin/bookings', methods=['GET'])
def get_all_bookings():
    try:
        bookings = mongo.db['Bookings'].find()
        booking_list = [
            {
                "_id": str(booking["_id"]),
                "customer_name": mongo.db['User'].find_one({"_id": booking["customer_id"]})["full_name"],
                "venue_name": mongo.db['VenueProvider'].find_one({"_id": booking["venue_id"]})["name_of_venue"],
                "booking_date_range": booking["booking_date_range"],
                "status": booking["status"]
            }
            for booking in bookings
        ]
        return jsonify({"bookings": booking_list}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR