import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_USERNAME=os.getenv('MONGO_USERNAME')
    MONGO_PASSWORD=os.getenv('MONGO_PASSWORD')
    MONGO_CLUSTER=os.getenv('MONGO_CLUSTER')
    MONGO_AUTHSOURCE=os.getenv('MONGO_AUTHSOURCE')
    MONGO_AUTHMECHANISM=os.getenv('MONGO_AUTHMECHANISM')
    MONGO_URI='mongodb+srv://' + MONGO_USERNAME + ':' + MONGO_PASSWORD + '@' + MONGO_CLUSTER + '/eeve_db?authSource=' + MONGO_AUTHSOURCE + '&authMechanism=' + MONGO_AUTHMECHANISM
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MAILJET_API_KEY = os.getenv('MAILJET_API_KEY')
    MAILJET_SECRET_KEY = os.getenv('MAILJET_SECRET_KEY')
    IMAGEKIT_PUBLIC_KEY = os.getenv('IMAGEKIT_PUBLIC_KEY')
    IMAGEKIT_PRIVATE_KEY = os.getenv('IMAGEKIT_PRIVATE_KEY')
    IMAGEKIT_URL_ENDPOINT = os.getenv('IMAGEKIT_URL_ENDPOINT')
    STRIPE_TEST_PUBLISHABLE_KEY = os.getenv('STRIPE_TEST_PUBLISHABLE_KEY')
    STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_TEST_SECRET_KEY')
    