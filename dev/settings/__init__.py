# settings/__init__.py
from flask import Blueprint

settings = Blueprint('settings', __name__)

from . import routes
