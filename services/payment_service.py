import stripe
from config import Config

class PaymentIntentService:
    def __init__(self):
        # Set the Stripe API key directly on the stripe module
        stripe.api_key = Config.STRIPE_TEST_SECRET_KEY

    def create_payment_intent(self, amount):
        try:
            # Convert amount to cents (Stripe uses smallest currency unit)
            amount_in_cents = int(amount * 100)

            result = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",
                automatic_payment_methods={"enabled": True},  # Enable automatic payment methods (like cards)
            )
            return result
        
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            raise Exception(f"Stripe Error: {str(e)}")

        except Exception as e:
            raise Exception(f"Payment Failed: {str(e)}")
