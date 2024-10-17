from flask_pymongo import PyMongo
from bson import ObjectId
from models import mongo

def get_user_id_by_email(email):
    """Retrieve the user ID based on the provided email."""
    try:
        user = mongo.db['User'].find_one({"email": email})
        if user:
            return str(user['_id'])  # Convert ObjectId to string
        else:
            return None
    except Exception as e:
        print("Error fetching user ID:", e)
        return None

class VenueProvider:
    def __init__(self, first_name, last_name, email, phone, id, name_of_venue, website, type_of_property, city, address, state, capacity, size, pin_location, place_description, created_by, cover_picture=None, other_property_type=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.id = id
        self.name_of_venue = name_of_venue
        self.website = website
        self.type_of_property = type_of_property
        self.other_property_type = other_property_type
        self.cover_picture = cover_picture
        self.city = city
        self.address = address
        self.state = state
        self.capacity = capacity
        self.size = size
        self.pin_location = pin_location
        self.place_description = place_description
        self.created_by = created_by

    def save(self):
        venue_data = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "id": self.id,
            "name_of_venue": self.name_of_venue,
            "website": self.website,
            "type_of_property": self.type_of_property,
            "other_property_type": self.other_property_type,
            "cover_picture": self.cover_picture,
            "city": self.city,
            "address": self.address,
            "state": self.state,
            "capacity": self.capacity,
            "size": self.size,
            "pin_location": self.pin_location,
            "place_description": self.place_description,
            "created_by": self.created_by
        }
        try:
            result = mongo.db['VenueProvider'].insert_one(venue_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e
    
    @staticmethod
    def find_by_id(venue_id):
        try:
            venue = mongo.db['VenueProvider'].find_one({"_id": ObjectId(venue_id)})
            if venue:
                venue['_id'] = str(venue['_id'])
            return venue
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_all():
        try:
            venues = mongo.db['VenueProvider'].find()
            return [{**venue, '_id': str(venue['_id'])} for venue in venues]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def update(venue_id, update_data):
        try:
            return mongo.db['VenueProvider'].update_one({'_id': ObjectId(venue_id)}, {'$set': update_data})
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete(venue_id):
        try:
            return mongo.db['VenueProvider'].delete_one({'_id': ObjectId(venue_id)})
        except Exception as e:
            print(str(e))
            return e

class VenuePricing:
    def __init__(self, venue_id, type, price):
        self.venue_id = venue_id
        self.type = type
        self.price = price

    def save(self):
        pricing_data = {
            "venue_id": ObjectId(self.venue_id),
            "type": self.type,
            "price": self.price
        }
        try:
            return mongo.db['VenuePricing'].insert_one(pricing_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            pricing = mongo.db['VenuePricing'].find({"venue_id": ObjectId(venue_id)})
            return {item['type']: item['price'] for item in pricing}
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete_by_venue_id(venue_id):
        try:
            return mongo.db['VenuePricing'].delete_many({"venue_id": ObjectId(venue_id)})
        except Exception as e:
            print(str(e))
            return e

class VenuePictures:
    def __init__(self, venue_id, image_url):
        self.venue_id = venue_id
        self.image_url = image_url

    def save(self):
        picture_data = {
            "venue_id": ObjectId(self.venue_id),
            "image_url": self.image_url
        }
        try:
            return mongo.db['VenuePictures'].insert_one(picture_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            pictures = mongo.db['VenuePictures'].find({"venue_id": ObjectId(venue_id)})
            return [picture['image_url'] for picture in pictures]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete_by_venue_id(venue_id):
        try:
            return mongo.db['VenuePictures'].delete_many({"venue_id": ObjectId(venue_id)})
        except Exception as e:
            print(str(e))
            return e

class VenueAdditionalService:
    def __init__(self, venue_id, service):
        self.venue_id = venue_id
        self.service = service

    def save(self):
        service_data = {
            "venue_id": ObjectId(self.venue_id),
            "service": self.service
        }
        try:
            return mongo.db['VenueAdditionalServices'].insert_one(service_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            services = mongo.db['VenueAdditionalServices'].find({"venue_id": ObjectId(venue_id)})
            return [service['service'] for service in services]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete_by_venue_id(venue_id):
        try:
            return mongo.db['VenueAdditionalServices'].delete_many({"venue_id": ObjectId(venue_id)})
        except Exception as e:
            print(str(e))
            return e

class VenueAmenity:
    def __init__(self, venue_id, amenity):
        self.venue_id = venue_id
        self.amenity = amenity

    def save(self):
        amenity_data = {
            "venue_id": ObjectId(self.venue_id),
            "amenity": self.amenity
        }
        try:
            return mongo.db['VenueAmenities'].insert_one(amenity_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_venue_id(venue_id):
        try:
            amenities = mongo.db['VenueAmenities'].find({"venue_id": ObjectId(venue_id)})
            return [amenity['amenity'] for amenity in amenities]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete_by_venue_id(venue_id):
        try:
            return mongo.db['VenueAmenities'].delete_many({"venue_id": ObjectId(venue_id)})
        except Exception as e:
            print(str(e))
            return e
