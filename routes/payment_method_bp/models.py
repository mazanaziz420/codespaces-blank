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
            return [{**payment, '_id': str(payment['_id'])} for payment in payments]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_user_id(user_id):
        try:
            payments = mongo.db['Payments'].find({"user_id": ObjectId(user_id)})
            return [{**payment, '_id': str(payment['_id'])} for payment in payments]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_stripe_payment_id(stripe_payment_id):
        try:
            payment = mongo.db['Payments'].find_one({"stripe_payment_id": stripe_payment_id})
            if payment:
                payment['_id'] = str(payment['_id'])
            return payment
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_status(payment_status):
        try:
            payments = mongo.db['Payments'].find({"payment_status": payment_status})
            return [{**payment, '_id': str(payment['_id'])} for payment in payments]
        except Exception as e:
            print(str(e))
            return e
