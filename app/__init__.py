"""Flask application factory."""
import os
from flask import Flask

from app.config import Config


def create_app(test_config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.update(test_config)
    
    # Register blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)
    
    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    return app