from bson import ObjectId
from datetime import datetime
from models import mongo

class Booking:
    def __init__(self, customer_id, venue_id, booking_date_range, status='pending'):
        self.customer_id = ObjectId(customer_id)
        self.venue_id = ObjectId(venue_id)
        self.booking_date_range = booking_date_range
        self.status = status
        self.requested_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def save(self):
        booking_data = {
            "customer_id": self.customer_id,
            "venue_id": self.venue_id,
            "booking_date_range": self.booking_date_range,
            "status": self.status,
            "requested_at": self.requested_at,
            "updated_at": self.updated_at
        }
        try:
            result = mongo.db['Bookings'].insert_one(booking_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            bookings = mongo.db['Bookings'].find({"venue_id": ObjectId(venue_id)})
            return [{**booking, '_id': str(booking['_id'])} for booking in bookings]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_customer_id(customer_id):
        try:
            bookings = mongo.db['Bookings'].find({"customer_id": ObjectId(customer_id)})
            return [{**booking, '_id': str(booking['_id'])} for booking in bookings]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def update_status(booking_id, new_status):
        try:
            return mongo.db['Bookings'].update_one(
                {'_id': ObjectId(booking_id)},
                {'$set': {'status': new_status, 'updated_at': datetime.utcnow()}}
            )
        except Exception as e:
            print(str(e))
            return e

class Notification:
    def __init__(self, user_id, message, venue_id, booking_id, is_read=False):
        self.user_id = ObjectId(user_id)
        self.message = message
        self.venue_id = ObjectId(venue_id)  # Can be a booking or venue ID
        self.booking_id = ObjectId(booking_id)
        self.is_read = is_read
        self.created_at = datetime.utcnow()

    def save(self):
        notification_data = {
            "user_id": self.user_id,
            "message": self.message,
            "venue_id": self.venue_id,
            "booking_id": self.booking_id,
            "is_read": self.is_read,
            "created_at": self.created_at
        }
        try:
            result = mongo.db['Notifications'].insert_one(notification_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_user_id(user_id, is_read=None):
        query = {"user_id": ObjectId(user_id)}
        if is_read is not None:
            query["is_read"] = is_read
        try:
            notifications = mongo.db['Notifications'].find(query).sort("created_at", -1)
            return [{**notification, '_id': str(notification['_id'])} for notification in notifications]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def mark_as_read(notification_id):
        try:
            return mongo.db['Notifications'].update_one(
                {'_id': ObjectId(notification_id)},
                {'$set': {'is_read': True}}
            )
        except Exception as e:
            print(str(e))
            return e