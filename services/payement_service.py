from stripe import StripeClient
from config import Config

class PaymentIntentService:
    def __init__(self):
        self.client = StripeClient(Config.STRIPE_TEST_SECRET_KEY)
        
    def create_payement_intent(self, amount, payment_method):
        try:
            result = self.client.PaymentIntent.create(
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
    
    