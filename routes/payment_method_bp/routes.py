# routes/payment_method_bp/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import PaymentMethod
from utils import HttpCodes
from bson import ObjectId
from models import mongo
from routes.helpers import is_customer, is_venue_provider


payment_method_bp = Blueprint('payment_method_bp', __name__)

@payment_method_bp.route('/add', methods=['POST'])
@jwt_required()
def add_payment_method():
    """Add a new payment method for the logged-in user."""
    current_user_email = get_jwt_identity()
    current_user = mongo.db['User'].find_one({"email": current_user_email['email']})

    # if not is_customer(current_user) or not is_venue_provider(current_user):
    #     return jsonify({"message": "Access denied. Only customers and venue providers can add payment methods."}), HttpCodes.HTTP_403_NOT_VERIFIED

    data = request.json
    payment_method = PaymentMethod(
        user_id=str(current_user['_id']),
        user_type=data['user_type'],
        card_holder_name=data['card_holder_name'],
        card_number=data['card_number'],
        card_expiry=data['card_expiry'],
        card_cvv=data['card_cvv'],
        card_type=data['card_type']
    )
    
    result = payment_method.save()
    if isinstance(result, ObjectId):
        return jsonify({"message": "Payment method added successfully"}), HttpCodes.HTTP_201_OK
    return jsonify({"error": "Failed to add payment method"}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@payment_method_bp.route('/get', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get all payment methods for the logged-in user."""
    try:
        current_user_email = get_jwt_identity()
        current_user = mongo.db['User'].find_one({"email": current_user_email['email']})
        if current_user is None:
            return jsonify({"error": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

        # if not is_customer(current_user):
        #     return jsonify({"message": "Access denied. Only customers can view payment methods."}), HttpCodes.HTTP_403_NOT_VERIFIED

        payment_methods = PaymentMethod.find_by_user_id(str(current_user['_id']))
        if payment_methods:
            return jsonify({"payment_methods": payment_methods}), HttpCodes.HTTP_200_OK
        else:
            return jsonify({"payment_methods": []}), HttpCodes.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({"message": "Failed to get payment methods", "error": str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@payment_method_bp.route('/update/<payment_id>', methods=['PUT'])
@jwt_required()
def update_payment_method(payment_id):
    """Update an existing payment method for the logged-in user."""
    current_user_email = get_jwt_identity()
    current_user = mongo.db['User'].find_one({"email": current_user_email['email']})

    if not is_customer(current_user):
        return jsonify({"message": "Access denied. Only customers can update payment methods."}), HttpCodes.HTTP_403_NOT_VERIFIED

    data = request.json
    result = PaymentMethod.update(payment_id, data)

    if result.matched_count > 0:
        return jsonify({"message": "Payment method updated successfully"}), HttpCodes.HTTP_200_OK
    return jsonify({"error": "Failed to update payment method"}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@payment_method_bp.route('/delete/<payment_id>', methods=['DELETE'])
@jwt_required()
def delete_payment_method(payment_id):
    """Delete a payment method for the logged-in user."""
    current_user_email = get_jwt_identity()
    current_user = mongo.db['User'].find_one({"email": current_user_email['email']})

    if not is_customer(current_user):
        return jsonify({"message": "Access denied. Only customers can delete payment methods."}), HttpCodes.HTTP_403_NOT_VERIFIED

    result = PaymentMethod.delete(payment_id)
    if result.deleted_count > 0:
        return jsonify({"message": "Payment method deleted successfully"}), HttpCodes.HTTP_200_OK
    return jsonify({"error": "Failed to delete payment method"}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
