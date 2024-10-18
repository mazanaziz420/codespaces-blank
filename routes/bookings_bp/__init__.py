from flask import Blueprint

bookings_bp = Blueprint('bookings_bp', __name__)

from . import routes