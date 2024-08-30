from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import *
from ..helpers import *
from utils import HttpCodes

vendor_bp = Blueprint('vendor_bp', __name__)

@vendor_bp.route('/vendor', methods=['POST'])
@jwt_required()
def create_vendor():
    auth_check = check_user_type('VENDOR')
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
        vendor = Vendor(
            category=data.get('selectedCategory'),
            subcategory=data.get('subcategory'),
            name=data.get('name'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zipCode'),
            address=data.get('address'),
            door_to_door_service=data.get('doorToDoorService') == 'true',
            description=data.get('description'),
            cover_picture=cover_picture_url
        )
        vendor_id = vendor.save()

        if isinstance(vendor_id, Exception):
            return jsonify({"message": "Error in Creating Vendor", "error": str(vendor_id)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

        for url in venue_pictures_urls:
            VendorPicture(vendor_id=vendor_id, image_url=url).save()
            
        return jsonify({"message": "Successfully Created"}), HttpCodes.HTTP_201_OK

    except Exception as e:
        return jsonify({"message": "Error processing data", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@vendor_bp.route('/vendor', methods=['GET'])
@jwt_required()
def get_vendors():
    try:
        vendors = Vendor.find_all()
        for vendor in vendors:
            vendor_id = vendor['_id']
            vendor['venue_pictures'] = VendorPicture.find_by_vendor_id(vendor_id)
        return jsonify(vendors), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error in Fetching Vendors", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@vendor_bp.route('/vendor/<vendor_id>', methods=['GET'])
@jwt_required()
def get_vendor(vendor_id):
    try:
        vendor = Vendor.find_by_id(vendor_id)
        if not vendor:
            return jsonify({"message": "Vendor not found"}), HttpCodes.HTTP_404_NOT_FOUND
        vendor['venue_pictures'] = VendorPicture.find_by_vendor_id(vendor_id)
        return jsonify(vendor), HttpCodes.HTTP_200_OK
    except Exception as e:
        return jsonify({"message": "Error in Fetching Vendor", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@vendor_bp.route('/vendor/<vendor_id>', methods=['PUT'])
@jwt_required()
def update_vendor(vendor_id):
    auth_check = check_user_type('VENDOR')
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
        update_data = {
            "category": data.get('selectedCategory'),
            "subcategory": data.get('subcategory'),
            "name": data.get('name'),
            "city": data.get('city'),
            "state": data.get('state'),
            "zip_code": data.get('zipCode'),
            "address": data.get('address'),
            "door_to_door_service": data.get('doorToDoorService') == 'true',
            "description": data.get('description'),
            "cover_picture": cover_picture_url
        }

        result = Vendor.update(vendor_id, update_data)

        if isinstance(result, Exception):
            return jsonify({"message": "Error in Updating Vendor", "error": str(result)}), 

        VendorPicture.delete_by_vendor_id(vendor_id)
        for url in venue_pictures_urls:
            VendorPicture(vendor_id=vendor_id, image_url=url).save()
            
        return jsonify({"message": "Successfully Updated"}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error processing data", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@vendor_bp.route('/vendor/<vendor_id>', methods=['DELETE'])
@jwt_required()
def delete_vendor(vendor_id):
    auth_check = check_user_type('VENDOR')
    if auth_check:
        return auth_check
    
    try:
        result = Vendor.delete(vendor_id)
        if result.deleted_count == 0:
            return jsonify({"message": "Vendor not found"}), HttpCodes.HTTP_404_NOT_FOUND
        VendorPicture.delete_by_vendor_id(vendor_id)
        return jsonify({"message": "Vendor deleted successfully"}), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({"message": "Error deleting vendor", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR