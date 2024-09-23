from flask_jwt_extended import create_access_token as jwt_create_access_token, get_jwt_identity
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

def check_if_admin():
    try:
        # Get the current user's email from the JWT token
        logged_in_email = get_jwt_identity()

        # Find the user by their email
        user = User.find_by_email(logged_in_email)

        # If the user doesn't exist, return False
        if not user:
            return False

        # Check if the user is an admin (assumed that 'user_type' indicates the role)
        if user.get('user_type') == 'ADMIN':  # Adjust this according to your role structure
            return True

        return False
    except Exception as e:
        print(f"Error in admin check: {str(e)}")
        return False