from flask_pymongo import PyMongo
from bson import ObjectId
from models import mongo

class Vendor:
    def __init__(self, category, subcategory, name, city, state, zip_code, address, door_to_door_service, description, cover_picture=None):
        self.category = category
        self.subcategory = subcategory
        self.name = name
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.address = address
        self.door_to_door_service = door_to_door_service
        self.description = description
        self.cover_picture = cover_picture

    def save(self):
        vendor_data = {
            "category": self.category,
            "subcategory": self.subcategory,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "address": self.address,
            "door_to_door_service": self.door_to_door_service,
            "description": self.description,
            "cover_picture": self.cover_picture,
        }
        try:
            result = mongo.db['Vendors'].insert_one(vendor_data)
            return result.inserted_id
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_all():
        try:
            vendors = mongo.db['Vendors'].find()
            return [{**vendor, '_id': str(vendor['_id'])} for vendor in vendors]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_id(vendor_id):
        try:
            vendor = mongo.db['Vendors'].find_one({"_id": ObjectId(vendor_id)})
            if vendor:
                vendor['_id'] = str(vendor['_id'])
            return vendor
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def update(vendor_id, update_data):
        try:
            return mongo.db['Vendors'].update_one({'_id': ObjectId(vendor_id)}, {'$set': update_data})
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete(vendor_id):
        try:
            return mongo.db['Vendors'].delete_one({'_id': ObjectId(vendor_id)})
        except Exception as e:
            print(str(e))
            return e

class VendorPicture:
    def __init__(self, vendor_id, image_url):
        self.vendor_id = vendor_id
        self.image_url = image_url

    def save(self):
        picture_data = {
            "vendor_id": ObjectId(self.vendor_id),
            "image_url": self.image_url,
        }
        try:
            return mongo.db['VendorPictures'].insert_one(picture_data)
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def find_by_vendor_id(vendor_id):
        try:
            pictures = mongo.db['VendorPictures'].find({"vendor_id": ObjectId(vendor_id)})
            return [picture['image_url'] for picture in pictures]
        except Exception as e:
            print(str(e))
            return e

    @staticmethod
    def delete_by_vendor_id(vendor_id):
        try:
            return mongo.db['VendorPictures'].delete_many({"vendor_id": ObjectId(vendor_id)})
        except Exception as e:
            print(str(e))
            return e
