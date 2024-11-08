from flask import Blueprint

staff_bp = Blueprint('staff_bp', __name__)

from . import routes