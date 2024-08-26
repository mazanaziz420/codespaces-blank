from flask_pymongo import PyMongo
from urllib.parse import quote_plus
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

mongo = PyMongo()

def init_app(app):
    app.config["MONGO_URI"] = Config.MONGO_URI
    mongo.init_app(app)

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

class VenueProvider:
    def __init__(self, property, name_of_place, city, state, postal_code, address, pin_location, additional_service, price, amenities, place_description, cover_picture=None, picture_of_venue=None):
        self.property = property
        self.name_of_place = name_of_place
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.address = address
        self.pin_location = pin_location
        self.additional_service = additional_service
        self.price = price
        self.amenities = amenities
        self.place_description = place_description
        self.cover_picture = cover_picture
        self.picture_of_venue = picture_of_venue

    def save(self):
        venue_data = {
            "property": self.property,
            "name_of_place": self.name_of_place,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "address": self.address,
            "pin_location": self.pin_location,
            "additional_service": self.additional_service,
            "price": self.price,
            "amenities": self.amenities,
            "place_description": self.place_description,
            "cover_picture": self.cover_picture,
            "picture_of_venue": self.picture_of_venue
        }
        try:
            return mongo.db['VenueProvider'].insert_one(venue_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_all():
        try:
            venues = mongo.db['VenueProvider'].find()
            # Convert ObjectId to string
            return [{**venue, '_id': str(venue['_id'])} for venue in venues]
        except Exception as e:
            print(str(e))
            return e