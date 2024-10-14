# models/payment.py
from bson import ObjectId
from models import mongo
from datetime import datetime

class Payment:
    def __init__(self, user_id, amount, currency, payment_method, payment_status, stripe_payment_id, created_at=None):
        self.user_id = ObjectId(user_id)
        self.amount = amount
        self.currency = currency
        self.payment_method = payment_method
        self.payment_status = payment_status
        self.stripe_payment_id = stripe_payment_id
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        payment_data = {
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "stripe_payment_id": self.stripe_payment_id,
            "created_at": self.created_at
        }
        try:
            result = mongo.db['Payments'].insert_one(payment_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_all():
        try:
            payments = mongo.db['Payments'].find()
            return [
                {
                    **payment, 
                    '_id': str(payment['_id']),  # Convert ObjectId to string
                    'user_id': str(payment['user_id']),  # Convert ObjectId to string
                } for payment in payments
            ]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_user_id(user_id):
        try:
            payments = mongo.db['Payments'].find({"user_id": ObjectId(user_id)})
            return [
                {
                    **payment, 
                    '_id': str(payment['_id']),
                    'user_id': str(payment['user_id']),  # Convert ObjectId to string
                } for payment in payments
            ]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_stripe_payment_id(stripe_payment_id):
        try:
            payment = mongo.db['Payments'].find_one({"stripe_payment_id": stripe_payment_id})
            if payment:
                payment['_id'] = str(payment['_id'])
                payment['user_id'] = str(payment['user_id'])  # Convert ObjectId to string
            return payment
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_status(payment_status):
        try:
            payments = mongo.db['Payments'].find({"payment_status": payment_status})
            return [
                {
                    **payment, 
                    '_id': str(payment['_id']),
                    'user_id': str(payment['user_id']),  # Convert ObjectId to string
                } for payment in payments
            ]
        except Exception as e:
            print(str(e))
            return e

class PayedVenues:
    def __init__(self, payment_id, venue_id, created_at=None):
        self.payment_id = payment_id
        self.venue_id = ObjectId(venue_id)
        self.created_at = created_at or datetime.utcnow()

    def save(self):
        venue_payment_data = {
            "payment_id": self.payment_id,
            "venue_id": self.venue_id,
            "created_at": self.created_at
        }
        try:
            result = mongo.db['VenuePayments'].insert_one(venue_payment_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            venue_payments = mongo.db['VenuePayments'].find({"venue_id": ObjectId(venue_id)})
            return [
                {
                    **vp, 
                    '_id': str(vp['_id']),
                    'venue_id': str(vp['venue_id']),  # Convert ObjectId to string
                } for vp in venue_payments
            ]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_payment_id(payment_id):
        try:
            venue_payment = mongo.db['VenuePayments'].find_one({"payment_id": ObjectId(payment_id)})
            if venue_payment:
                venue_payment['_id'] = str(venue_payment['_id'])
                venue_payment['venue_id'] = str(venue_payment['venue_id'])  # Convert ObjectId to string
            return venue_payment
        except Exception as e:
            print(str(e)) 
            return e 
        