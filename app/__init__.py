"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from app.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(test_config=None):
    """Create and configure Flask application."""
    app = Flask(__name__)

    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.update(test_config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # Import models for migration detection
    from app.models import User  # noqa: F401

    # User loader callback for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """Load user from the database for Flask-Login session management."""
        return User.query.get(int(user_id))

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Register blueprints
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # Register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Test database connection on startup
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text('SELECT 1'))
            app.logger.info('Database connection successful')
        except Exception as e:
            app.logger.error(f'Database connection failed: {e}')

    return app
