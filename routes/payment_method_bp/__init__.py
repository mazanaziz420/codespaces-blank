from flask import Blueprint

payment_method_bp = Blueprint('payment_method_bp', __name__)

from . import routes