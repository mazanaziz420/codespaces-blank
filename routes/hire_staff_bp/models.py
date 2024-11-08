from bson import ObjectId
from datetime import datetime
from models import mongo

class HireRequest:
    def __init__(self, staff_id, hirer_id, hirer_type, requested_dates, status='pending'):
        self.staff_id = ObjectId(staff_id)
        self.hirer_id = ObjectId(hirer_id)
        self.hirer_type = hirer_type  # 'customer' or 'venue_provider'
        self.requested_dates = requested_dates
        self.status = status
        self.requested_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def save(self):
        hire_request_data = {
            "staff_id": self.staff_id,
            "hirer_id": self.hirer_id,
            "hirer_type": self.hirer_type,
            "requested_dates": self.requested_dates,
            "status": self.status,
            "requested_at": self.requested_at,
            "updated_at": self.updated_at
        }
        result = mongo.db['HireRequests'].insert_one(hire_request_data)
        return result.inserted_id

    @staticmethod
    def update_status(hire_request_id, new_status):
        return mongo.db['HireRequests'].update_one(
            {"_id": ObjectId(hire_request_id)},
            {"$set": {"status": new_status, "updated_at": datetime.utcnow()}}
        )

    @staticmethod
    def find_by_staff_id(staff_id):
        return list(mongo.db['HireRequests'].find({"staff_id": ObjectId(staff_id)}))

    @staticmethod
    def find_by_hirer_id(hirer_id):
        return list(mongo.db['HireRequests'].find({"hirer_id": ObjectId(hirer_id)}))
    
    @staticmethod
    def find_by_id(hire_request_id):
        return list(mongo.db['HireRequests'].find({"_id": ObjectId(hire_request_id)}))
    
