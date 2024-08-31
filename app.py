from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import init_app
from routes.users_bp.routes import users_bp
from routes.venue_provider_bp.routes import venue_provider_bp
from routes.vendor_bp.routes import vendor_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

jwt = JWTManager(app)

init_app(app)

app.register_blueprint(users_bp, url_prefix='/')
app.register_blueprint(venue_provider_bp, url_prefix='/venueProvider')
app.register_blueprint(vendor_bp, url_prefix='/vendor')

if __name__ == '__main__':
    app.run(debug=True)
