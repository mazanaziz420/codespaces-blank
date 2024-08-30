from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.image_upload_service import ImageUploadingService
from .models import *
from utils import HttpCodes
import json

venue_provider_bp = Blueprint('venue_provider_bp', __name__)
image_upload_service = ImageUploadingService()

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

@venue_provider_bp.route('/postdata', methods=['POST'])
@jwt_required()
def create_venue_provider():
    current_user = get_jwt_identity()
    data = request.form
    files = request.files
    print("Form Data:", dict(data))  # Convert to dict for better readability
    print("Files:", {k: v.filename for k, v in files.items()})

    

    cover_picture_url = None
    venue_pictures_urls = []

    try:
        if 'coverPicture' in files:
            cover_picture = files['coverPicture']
            secure_name = secure_filename(cover_picture.filename)
            cover_picture_url = image_upload_service.upload_image(
                file=cover_picture.read(),
                file_name=secure_name
            )

        if 'venuePictures' in files:
            for file in request.files.getlist('venuePictures'):
                secure_name = secure_filename(file.filename)
                url = image_upload_service.upload_image(
                    file=file.read(),
                    file_name=secure_name
                )
                venue_pictures_urls.append(url)

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

@venue_provider_bp.route('/<venue_id>', methods=['DELETE'])
@jwt_required()
def delete_venue_provider(venue_id):
    current_user = get_jwt_identity()
    try:
        # Delete the venue
        result = mongo.db['VenueProvider'].delete_one({'_id': ObjectId(venue_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "Venue not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # Delete associated pricing
        mongo.db['VenuePricing'].delete_many({'venue_id': ObjectId(venue_id)})

        # Delete associated amenities
        mongo.db['VenueAmenities'].delete_many({'venue_id': ObjectId(venue_id)})

        # Delete associated additional services
        mongo.db['VenueAdditionalServices'].delete_many({'venue_id': ObjectId(venue_id)})

        # Delete associated pictures
        mongo.db['VenuePictures'].delete_many({'venue_id': ObjectId(venue_id)})

        return jsonify({"message": "Venue and associated data deleted successfully"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error deleting venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
