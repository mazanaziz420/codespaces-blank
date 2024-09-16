import stripe

stripe.api_key="sk_test_51PzidUP7IPyRWGaH8kN3GQKAiylpju3FgqHC3Nh1pFhPfRCT6ZNjdX1B8VlygDbKGzEJ4qNERD0M7P4Ru9MueukL004pQqhTUX"

payment = stripe.PaymentIntent.create(
  amount=2000,
  currency="usd",
  automatic_payment_methods={"enabled": True},
)

print(payment)