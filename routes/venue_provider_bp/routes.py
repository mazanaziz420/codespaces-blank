from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from utils import HttpCodes
import json
from .models import *
from .helpers import *

venue_provider_bp = Blueprint('venue_provider_bp', __name__)

@venue_provider_bp.route('/postdata', methods=['POST'])
@jwt_required()
def create_venue_provider():
    auth_check = check_user_type('VENUE_PROVIDER')
    if auth_check:
        return auth_check
    
    data = request.form
    files = request.files
    cover_picture_url = None
    venue_pictures_urls = []
    
    try:
        if 'coverPicture' in files:
            cover_picture_url = upload_image(files['coverPicture'])

        if 'venuePictures' in files:
            venue_pictures_urls = [upload_image(file) for file in request.files.getlist('venuePictures')]

    except Exception as e:
        return jsonify({"message": "File upload failed", "error": str(e)}), HttpCodes.HTTP_400_BAD_REQUEST

    try:
        venue_provider = VenueProvider(
            first_name=data.get('firstName'),
            last_name=data.get('lastName'),
            email=data.get('email'),
            phone=data.get('phone'),
            id=data.get('id'),
            name_of_venue=data.get('nameOfVenue'),
            website=data.get('website'),
            type_of_property=data.get('typeOfProperty'),
            other_property_type=data.get('otherPropertyType'),
            cover_picture=cover_picture_url,
            city=data.get('city'),
            address=data.get('address'),
            state=data.get('state'),
            capacity=int(data.get('capacity')),
            size=int(data.get('size')),
            pin_location=data.get('pinLocation'),
            place_description=data.get('placeDescription')
        )
        result = venue_provider.save()

        if isinstance(result, Exception):
            return jsonify({"message": "Error in Creating Venue", "error": str(result)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

        venue_provider_id = result.inserted_id
    
        # Save additional services
        additional_services = data.getlist('additionalServices')
        for service in additional_services:
            VenueAdditionalService(venue_id=venue_provider_id, service=service).save()

        # Save amenities
        amenities = data.getlist('amenities')
        for amenity in amenities:
            VenueAmenity(venue_id=venue_provider_id, amenity=amenity).save()

        # Save pricing
        pricing = json.loads(data.get('pricing'))
        if pricing:
            for type, price in pricing.items():
                VenuePricing(venue_id=venue_provider_id, type=type, price=price).save()

        # Save venue pictures
        for url in venue_pictures_urls:
            VenuePictures(venue_id=venue_provider_id, image_url=url).save()
        
        return jsonify({"message": "Successfully Created"}), HttpCodes.HTTP_201_OK

    except Exception as e:
        return jsonify({"message": "Error processing data", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/get/makeups', methods=['GET'])
@jwt_required()
def get_venue_providers():
    current_user = get_jwt_identity()
    try:
        venues = VenueProvider.find_all()
        for venue in venues:
            venue_id = venue['_id']
            print(venue_id)
            # Fetch related pricing
            venue['pricing'] = {
                pricing['type']: pricing['price']
                for pricing in mongo.db['VenuePricing'].find({"venue_id": ObjectId(venue_id)})
            }

            # Fetch related amenities
            venue['amenities'] = [
                amenity['amenity']
                for amenity in mongo.db['VenueAmenities'].find({"venue_id": ObjectId(venue_id)})
            ]

            # Fetch related additional services
            venue['additionalServices'] = [
                service['service']
                for service in mongo.db['VenueAdditionalServices'].find({"venue_id": ObjectId(venue_id)})
            ]

            # Fetch related pictures
            venue['venuePictures'] = [
                picture['image_url']
                for picture in mongo.db['VenuePictures'].find({"venue_id": ObjectId(venue_id)})
            ]

        return jsonify(venues), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error in Fetching Venues", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/updatedata/<venue_id>', methods=['PUT'])
@jwt_required()
def update_venue_provider(venue_id):
    current_user = get_jwt_identity()
    data = request.form
    files = request.files

    cover_picture_url = None
    venue_pictures_urls = []

    try:
        if 'coverPicture' in files:
            cover_picture_url = upload_image(files['coverPicture'])

        if 'venuePictures' in files:
            venue_pictures_urls = [upload_image(file) for file in request.files.getlist('venuePictures')]

        update_data = {
            "first_name": data.get('firstName'),
            "last_name": data.get('lastName'),
            "email": data.get('email'),
            "phone": data.get('phone'),
            "id": data.get('id'),
            "name_of_venue": data.get('nameOfVenue'),
            "website": data.get('website'),
            "cover_picture": cover_picture_url,
            "type_of_property": data.get('typeOfProperty'),
            "other_property_type": data.get('otherPropertyType'),
            "city": data.get('city'),
            "address": data.get('address'),
            "state": data.get('state'),
            "capacity": int(data.get('capacity')),
            "size": int(data.get('size')),
            "pin_location": data.get('pinLocation'),
            "place_description": data.get('placeDescription'),
        }

        result = mongo.db['VenueProvider'].update_one(
            {'_id': ObjectId(venue_id)},
            {'$set': update_data}
        )

        additional_services = data.getlist('additionalServices')
        if additional_services:
            mongo.db['VenueAdditionalServices'].delete_many({'venue_id': ObjectId(venue_id)})
            for service in additional_services:
                VenueAdditionalService(venue_id=venue_id, service=service).save()

        amenities = data.getlist('amenities')
        if amenities:
            mongo.db['VenueAmenities'].delete_many({'venue_id': ObjectId(venue_id)})
            for amenity in amenities:
                VenueAmenity(venue_id=venue_id, amenity=amenity).save()

        pricing = json.loads(data.get('pricing'))
        if pricing:
            mongo.db['VenuePricing'].delete_many({'venue_id': ObjectId(venue_id)})
            for type, price in pricing.items():
                VenuePricing(venue_id=venue_id, type=type, price=price).save()

        for url in venue_pictures_urls:
            VenuePictures(venue_id=venue_id, image_url=url).save()

        return jsonify({"message": "Successfully Updated"}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error updating venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/<venue_id>', methods=['DELETE'])
@jwt_required()
def delete_venue_provider(venue_id):
    current_user = get_jwt_identity()
    try:
        result = mongo.db['VenueProvider'].delete_one({'_id': ObjectId(venue_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "Venue not found"}), HttpCodes.HTTP_404_NOT_FOUND

        mongo.db['VenuePricing'].delete_many({'venue_id': ObjectId(venue_id)})

        mongo.db['VenueAmenities'].delete_many({'venue_id': ObjectId(venue_id)})

        mongo.db['VenueAdditionalServices'].delete_many({'venue_id': ObjectId(venue_id)})

        mongo.db['VenuePictures'].delete_many({'venue_id': ObjectId(venue_id)})

        return jsonify({"message": "Venue and associated data deleted successfully"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error deleting venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
