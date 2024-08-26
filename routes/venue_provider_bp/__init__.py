from flask import Blueprint

venue_provider_bp = Blueprint('venue_provider_bp', __name__)

from . import routes  # Import routes to register them
