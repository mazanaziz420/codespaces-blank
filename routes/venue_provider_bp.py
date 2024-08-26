from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.image_upload_service import ImageUploadingService
from models import *
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
    picture_of_venue_url = None

    try:
        if 'coverPicture' in files:
            cover_picture = files['coverPicture']
            secure_name = secure_filename(cover_picture.filename)
            cover_picture_url = image_upload_service.upload_image(
                file=cover_picture.read(),
                file_name=secure_name
            )

        if 'pictureOfVenue' in files:
            picture_of_venue = files['pictureOfVenue']
            secure_name = secure_filename(picture_of_venue.filename)
            picture_of_venue_url = image_upload_service.upload_image(
                file=picture_of_venue.read(),
                file_name=secure_name
            )

    except Exception as e:
        return jsonify({"message": "File upload failed", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

    venue_provider = VenueProvider(
        property=data.get('property'),
        name_of_place=data.get('nameOfPlace'),
        city=data.get('city'),
        state=data.get('state'),
        postal_code=int(data.get('postalCode')),
        address=data.get('address'),
        pin_location=int(data.get('pinLocation')),
        additional_service=data.get('additionalService'),
        price=float(data.get('price')),
        amenities=data.get('amenities'),
        place_description=data.get('placeDescription'),
        cover_picture=cover_picture_url,
        picture_of_venue=picture_of_venue_url
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