from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.image_upload_service import ImageUploadingService
from .models import *
from utils import HttpCodes

venue_provider_bp = Blueprint('venue_provider_bp', __name__)
image_upload_service = ImageUploadingService()

@venue_provider_bp.route('/get/makeups', methods=['GET'])
@jwt_required()
def get_venue_providers():
    current_user = get_jwt_identity()
    try:
        venues = VenueProvider.find_all()
        return jsonify(venues), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error in Fetching Venues", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@venue_provider_bp.route('/postdata', methods=['POST'])
@jwt_required()
def create_venue_provider():
    current_user = get_jwt_identity()
    data = request.form
    files = request.files

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
        return jsonify({"message": "File upload failed", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

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
        city=data.get('city'),
        address=data.get('address'),
        state=data.get('state'),
        capacity=int(data.get('capacity')),
        size=int(data.get('size')),
        pin_location=data.get('pinLocation'),
        place_description=data.get('placeDescription'),
        additional_services=data.get('additionalServices'),
        amenities=data.get('amenities'),
        pricing=data.get('pricing'),
        availability=data.get('availability'),
        rules_and_regulations=data.get('rulesAndRegulations'),
        special_features=data.get('specialFeatures'),
        cover_picture=cover_picture_url,
        venue_pictures=venue_pictures_urls
    )

    result = venue_provider.save()

    if isinstance(result, Exception):
        return jsonify({"message": "Error in Creating Venue", "error": str(result)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

    return jsonify({"message": "Successfully Created"}), HttpCodes.HTTP_201_OK

@venue_provider_bp.route('/<venue_id>', methods=['DELETE'])
@jwt_required()
def delete_venue_provider(venue_id):
    current_user = get_jwt_identity()
    try:
        result = mongo.db['VenueProvider'].delete_one({'_id': ObjectId(venue_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "Venue not found"}), HttpCodes.HTTP_404_NOT_FOUND
        return jsonify({"message": "Venue deleted successfully"}), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error deleting venue", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
