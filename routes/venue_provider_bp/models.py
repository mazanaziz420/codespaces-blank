from flask_pymongo import PyMongo
from bson import ObjectId
from models import mongo

class VenueProvider:
    def __init__(self, first_name, last_name, email, phone, id, name_of_venue, website, type_of_property, city, address, state, capacity, size, pin_location, place_description, cover_picture=None, other_property_type=None):
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
            "place_description": self.place_description
        }
        try:
            return mongo.db['VenueProvider'].insert_one(venue_data)
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

class VenuePricing:
    def __init__(self, venue_id, type, price):
        self.venue_id = venue_id
        self.type = type
        self.price = price

    def save(self):
        pricing_data = {
            "venue_id": self.venue_id,
            "type": self.type,
            "price": self.price
        }
        try:
            return mongo.db['VenuePricing'].insert_one(pricing_data)
        except Exception as e:
            print(str(e))
            return e

class VenuePictures:
    def __init__(self, venue_id, image_url):
        self.venue_id = venue_id
        self.image_url = image_url

    def save(self):
        picture_data = {
            "venue_id": self.venue_id,
            "image_url": self.image_url
        }
        try:
            return mongo.db['VenuePictures'].insert_one(picture_data)
        except Exception as e:
            print(str(e))
            return e

class VenueAdditionalService:
    def __init__(self, venue_id, service):
        self.venue_id = venue_id
        self.service = service

    def save(self):
        service_data = {
            "venue_id": self.venue_id,
            "service": self.service
        }
        try:
            return mongo.db['VenueAdditionalServices'].insert_one(service_data)
        except Exception as e:
            print(str(e))
            return e

class VenueAmenity:
    def __init__(self, venue_id, amenity):
        self.venue_id = venue_id
        self.amenity = amenity

    def save(self):
        amenity_data = {
            "venue_id": self.venue_id,
            "amenity": self.amenity
        }
        try:
            return mongo.db['VenueAmenities'].insert_one(amenity_data)
        except Exception as e:
            print(str(e))
            return e
