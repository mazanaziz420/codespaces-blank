from werkzeug.security import generate_password_hash, check_password_hash
from models import mongo

class User:
    def __init__(self, email, password, full_name, username, user_type, verification_code):
        self.email = email
        self.password = generate_password_hash(password)
        self.full_name = full_name
        self.username = username
        self.user_type = user_type
        self.verification_code = verification_code
        self.is_verified = False

    def save(self):
        user_data = {
            "email": self.email,
            "password": self.password,
            "full_name": self.full_name,
            "username": self.username,
            "user_type": self.user_type,
            "verification_code": self.verification_code,
            "is_verified": self.is_verified
        }
        try:
            return mongo.db['User'].insert_one(user_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_email(email):
        try:
            return mongo.db['User'].find_one({"email": email})
        except Exception as e:
            print(str(e))
            return e
        
    @staticmethod
    def verify_password(stored_password, provided_password):
        return check_password_hash(stored_password, provided_password)
