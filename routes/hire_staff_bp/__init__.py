from flask import Blueprint

hire_staff_bp = Blueprint('hire_staff_bp', __name__)

from . import routes