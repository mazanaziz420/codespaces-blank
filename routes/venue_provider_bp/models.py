from flask_pymongo import PyMongo
from bson import ObjectId
from models import mongo

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