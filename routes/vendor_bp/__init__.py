from flask import Blueprint

vendor_bp = Blueprint('vendor_bp', __name__)

from . import routes
