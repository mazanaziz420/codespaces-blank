# routes/payment_method_bp/routes.py
from flask import Blueprint, request, jsonify
from utils import HttpCodes
from services.payment_service import PaymentIntentService

payment_method_bp = Blueprint('payment_method_bp', __name__)
payment_service = PaymentIntentService()

@payment_method_bp.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    try:
        data = request.json
        amount = data.get('amount')

        if not amount:
            return jsonify({"message": "Missing amount"}), HttpCodes.HTTP_400_BAD_REQUEST

        # Create the payment intent with the amount
        result = payment_service.create_payment_intent(amount)

        return jsonify({
            'client_secret': result.client_secret,
            'status': result.status,
            'result': result
        }), HttpCodes.HTTP_200_OK

    except Exception as e:
        return jsonify({'error': str(e)}), HttpCodes.HTTP_400_BAD_REQUEST
