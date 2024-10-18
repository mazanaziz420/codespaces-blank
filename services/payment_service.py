import stripe
from config import Config
from routes.payments_bp.models import Payment

class PaymentIntentService:
    def __init__(self):
        stripe.api_key = Config.STRIPE_TEST_SECRET_KEY

    def create_payment_intent(self, user_id, amount, payment_method):
        try:
            amount_in_cents = int(float(amount) * 100)

            # Create a PaymentIntent on Stripe with the provided payment method
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency="usd",
                automatic_payment_methods={"enabled": True},
                # payment_method=payment_method,  # Attach the payment method from frontend
                # confirmation_method='manual',  # Confirm the payment manually
                # confirm=True  # Immediately confirm the payment
            )

            # Save payment to the database
            new_payment = Payment(
                user_id=user_id,
                amount=amount,
                currency="usd",
                payment_method=payment_method,  # Assuming card payment for this example
                payment_status=payment_intent.status,
                stripe_payment_id=payment_intent.id
            )
            new_payment.save()

            return payment_intent
        
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe Error: {str(e)}")

        except Exception as e:
            raise Exception(f"Payment Failed: {str(e)}")