from flask_jwt_extended import create_access_token as jwt_create_access_token
from routes.users_bp.models import User

def generate_access_token(email):
    user = User.find_by_email(email)
    if user:
        return jwt_create_access_token(identity={"email": user['email'], "user_type": user['user_type']})
    return None

def authenticate_user(email, password):
    user = User.find_by_email(email)
    if user and User.verify_password(user['password'], password):
        return user
    return None
