"""Main blueprint for application routes."""
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.blueprints.main import routes