"""API Blueprint initialization."""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them with the blueprint
from app.blueprints.api import routes  # noqa: F401
from app.blueprints.api import movies  # noqa: F401
from app.blueprints.api import subtitles  # noqa: F401
from app.blueprints.api import progress  # noqa: F401
from app.blueprints.api import bookmarks  # noqa: F401
from app.blueprints.api import dashboard  # noqa: F401
