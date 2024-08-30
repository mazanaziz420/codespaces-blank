from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from services.image_upload_service import ImageUploadingService
from utils import HttpCodes

image_upload_service = ImageUploadingService()

def upload_image(file):
    secure_name = secure_filename(file.filename)
    return image_upload_service.upload_image(file=file.read(), file_name=secure_name)

def check_user_type(required_type):
    current_user = get_jwt_identity()
    
    if not isinstance(current_user, dict):
        return jsonify({"message": "Invalid token"}), HttpCodes.HTTP_401_UNAUTHORIZED

    if current_user.get('user_type') != required_type:
        return jsonify({"message": "User not authorized"}), HttpCodes.HTTP_403_NOT_VERIFIED
    
    return None