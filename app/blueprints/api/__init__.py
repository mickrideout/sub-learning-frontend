"""API Blueprint initialization."""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them with the blueprint
from app.blueprints.api import routes  # noqa: F401
