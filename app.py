from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import init_app
from routes.users_bp.routes import users_bp
from routes.venue_provider_bp.routes import venue_provider_bp
from routes.vendor_bp.routes import vendor_bp
from routes.payments_bp.routes import payments_bp
from routes.bookings_bp.routes import bookings_bp
from routes.payment_method_bp.routes import payment_method_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

jwt = JWTManager(app)

init_app(app)

app.register_blueprint(users_bp, url_prefix='/')
app.register_blueprint(venue_provider_bp, url_prefix='/venueProvider')
app.register_blueprint(vendor_bp, url_prefix='/vendor')
app.register_blueprint(payments_bp, url_prefix='/payment')
app.register_blueprint(bookings_bp, url_prefix='/booking')
app.register_blueprint(payment_method_bp, url_prefix='/payment_method')

if __name__ == '__main__':
    app.run(debug=True)
