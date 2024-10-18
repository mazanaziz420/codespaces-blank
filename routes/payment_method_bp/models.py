# models/payment_method.py
from bson import ObjectId
from models import mongo

class PaymentMethod:
    def __init__(self, user_id, card_holder_name, card_number, card_expiry, card_cvv, card_type):
        self.user_id = ObjectId(user_id)
        self.card_holder_name = card_holder_name
        self.card_number = card_number
        self.card_expiry = card_expiry
        self.card_cvv = card_cvv
        self.card_type = card_type

    def save(self):
        payment_data = {
            "user_id": self.user_id,
            "card_holder_name": self.card_holder_name,
            "card_number": self.card_number,
            "card_expiry": self.card_expiry,
            "card_cvv": self.card_cvv,
            "card_type": self.card_type
        }
        try:
            result = mongo.db['PaymentMethods'].insert_one(payment_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_user_id(user_id):
        try:
            payment_methods = mongo.db['PaymentMethods'].find({"user_id": ObjectId(user_id)})
            return [{**method, '_id': str(method['_id'])} for method in payment_methods]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def update(payment_id, update_data):
        try:
            return mongo.db['PaymentMethods'].update_one({'_id': ObjectId(payment_id)}, {'$set': update_data})
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete(payment_id):
        try:
            return mongo.db['PaymentMethods'].delete_one({'_id': ObjectId(payment_id)})
        except Exception as e:
            print(str(e))
            return e
