from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from utils import HttpCodes
import json
from .models import *
from ..helpers import *

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
        venue_provider_id = venue_provider.save()

        if isinstance(venue_provider_id, Exception):
            return jsonify({"message": "Error in Creating Venue", "error": str(venue_provider_id)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
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
    try:
        venues = VenueProvider.find_all()
        for venue in venues:
            venue_id = venue['_id']

            # Fetch related pricing
            venue['pricing'] = VenuePricing.find_by_venue_id(venue_id)

            # Fetch related amenities
            venue['amenities'] = VenueAmenity.find_by_venue_id(venue_id)

            # Fetch related additional services
            venue['additionalServices'] = VenueAdditionalService.find_by_venue_id(venue_id)

            # Fetch related pictures
            venue['venuePictures'] = VenuePictures.find_by_venue_id(venue_id)

        return jsonify(venues), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error in Fetching Venues", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/get/makeup/<venue_provider_id>', methods=['GET'])
@jwt_required()
def get_venue_provider(venue_provider_id):
    try:
        venue = VenueProvider.find_by_id(venue_provider_id)
        if not venue:
            return jsonify({"message": "Venue not found"}), HttpCodes.HTTP_404_NOT_FOUND

        venue_id = venue['_id']

        # Fetch related pricing
        venue['pricing'] = VenuePricing.find_by_venue_id(venue_id)

        # Fetch related amenities
        venue['amenities'] = VenueAmenity.find_by_venue_id(venue_id)

        # Fetch related additional services
        venue['additionalServices'] = VenueAdditionalService.find_by_venue_id(venue_id)

        # Fetch related pictures
        venue['venuePictures'] = VenuePictures.find_by_venue_id(venue_id)

        return jsonify(venue), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error in Fetching Venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/updatedata/<venue_id>', methods=['PUT'])
@jwt_required()
def update_venue_provider(venue_id):
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

        result = VenueProvider.update(venue_id, update_data)

        if isinstance(result, Exception):
            return jsonify({"message": "Error in Updating Venue", "error": str(result)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

        # Update additional services
        additional_services = data.getlist('additionalServices')
        VenueAdditionalService.delete_by_venue_id(venue_id)
        for service in additional_services:
            VenueAdditionalService(venue_id=venue_id, service=service).save()

        # Update amenities
        amenities = data.getlist('amenities')
        VenueAmenity.delete_by_venue_id(venue_id)
        for amenity in amenities:
            VenueAmenity(venue_id=venue_id, amenity=amenity).save()

        # Update pricing
        pricing = json.loads(data.get('pricing'))
        VenuePricing.delete_by_venue_id(venue_id)
        if pricing:
            for type, price in pricing.items():
                VenuePricing(venue_id=venue_id, type=type, price=price).save()

        # Update venue pictures
        VenuePictures.delete_by_venue_id(venue_id)
        for url in venue_pictures_urls:
            VenuePictures(venue_id=venue_id, image_url=url).save()

        return jsonify({"message": "Successfully Updated"}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error updating venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/<venue_id>', methods=['DELETE'])
@jwt_required()
def delete_venue_provider(venue_id):
    try:
        result = VenueProvider.delete(venue_id)
        if result.deleted_count == 0:
            return jsonify({"message": "Venue not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Delete related records
        VenuePricing.delete_by_venue_id(venue_id)
        VenueAmenity.delete_by_venue_id(venue_id)
        VenueAdditionalService.delete_by_venue_id(venue_id)
        VenuePictures.delete_by_venue_id(venue_id)

        return jsonify({"message": "Venue and associated data deleted successfully"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error deleting venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
