import stripe
from config import Config

class PaymentIntentService:
    def __init__(self):
        # Set the Stripe API key directly on the stripe module
        stripe.api_key = Config.STRIPE_TEST_SECRET_KEY

    def create_payment_intent(self, amount, payment_method):
        try:
            result = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                payment_method=payment_method,
                confirmation_method='manual',
                confirm=True,
            )
            if result:
                return result
            else:
                raise Exception("Payment Method Failed")
        
        except Exception as e:
            raise Exception(f"Payment Failed: {str(e)}")
