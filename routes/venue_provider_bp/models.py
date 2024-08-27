from flask_pymongo import PyMongo
from bson import ObjectId
from models import mongo

class VenueProvider:
    def __init__(self, first_name, last_name, email, phone, id, name_of_venue, website, type_of_property, city, address, state, capacity, size, pin_location, place_description, additional_services, amenities, pricing, availability, rules_and_regulations, special_features, cover_picture=None, venue_pictures=None, other_property_type=None):
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
        self.venue_pictures = venue_pictures
        self.city = city
        self.address = address
        self.state = state
        self.capacity = capacity
        self.size = size
        self.pin_location = pin_location
        self.place_description = place_description
        self.additional_services = additional_services
        self.amenities = amenities
        self.pricing = pricing
        self.availability = availability
        self.rules_and_regulations = rules_and_regulations
        self.special_features = special_features

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
            "venue_pictures": self.venue_pictures,
            "city": self.city,
            "address": self.address,
            "state": self.state,
            "capacity": self.capacity,
            "size": self.size,
            "pin_location": self.pin_location,
            "place_description": self.place_description,
            "additional_services": self.additional_services,
            "amenities": self.amenities,
            "pricing": self.pricing,
            "availability": self.availability,
            "rules_and_regulations": self.rules_and_regulations,
            "special_features": self.special_features
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
