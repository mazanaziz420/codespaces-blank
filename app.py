from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # Import CORS
from config import Config
from models import init_app

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": "*"}})

jwt = JWTManager(app)

init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
