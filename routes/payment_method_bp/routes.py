# routes/payment_method_bp/routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from utils import HttpCodes
from services.payment_service import PaymentIntentService
from routes.users_bp.models import User
from .models import Payment

payment_method_bp = Blueprint('payment_method_bp', __name__)
payment_service = PaymentIntentService()

@payment_method_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount')
        email = data.get('email')
        payment_method = data.get('payment_method')

        if not amount or not email or not payment_method:
            return jsonify({"message": "Missing amount, email or payment method"}), HttpCodes.HTTP_400_BAD_REQUEST

        logged_in_identity = get_jwt_identity()
        logged_in_email = logged_in_identity.get("email")
        
        if email != logged_in_email:
            return jsonify({"message": "Unauthorized: Email mismatch"}), HttpCodes.HTTP_403_NOT_VERIFIED

        user = User.find_by_email(logged_in_email)

        if not user:
            return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

        result = payment_service.create_payment_intent(user['_id'], amount, payment_method)

        return jsonify({
            'client_secret': result.client_secret,
            'status': result.status,
            'result': result
        }), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_400_BAD_REQUEST

@payment_method_bp.route('/all_payments', methods=['GET'])
@jwt_required()
def get_all_payments():
    try:
        # if not check_if_admin():
        #     return jsonify({"message": "Unauthorized access"}), HttpCodes.HTTP_403_FORBIDDEN

        payments = Payment.find_all()

        return jsonify(payments), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
    
@payment_method_bp.route('/payment_by_user_id', methods=['GET'])
@jwt_required()
def get_user_payments():
    try:
        logged_in_email = get_jwt_identity()
        user = User.find_by_email(logged_in_email)

        if not user:
            return jsonify({"message": "User not found"}), HttpCodes.HTTP_404_NOT_FOUND

        payments = Payment.find_by_user_id(user['_id'])

        return jsonify(payments), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@payment_method_bp.route('/payment_by_stripe_id/<stripe_payment_id>', methods=['GET'])
@jwt_required()
def get_payment_by_stripe_id(stripe_payment_id):
    try:
        payment = Payment.find_by_stripe_payment_id(stripe_payment_id)

        if not payment:
            return jsonify({"message": "Payment not found"}), HttpCodes.HTTP_404_NOT_FOUND

        return jsonify(payment), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR

@payment_method_bp.route('/payment_by_status/<status>', methods=['GET'])
@jwt_required()
def get_payments_by_status(status):
    try:
        payments = Payment.find_by_status(status)

        if not payments:
            return jsonify({"message": "No payments found for this status"}), HttpCodes.HTTP_404_NOT_FOUND

        return jsonify(payments), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_500_INTERNAL_SERVER_ERROR
