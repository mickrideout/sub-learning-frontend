"""Centralized error handling for Flask application."""
from flask import jsonify, render_template, request
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    """Register error handlers with the Flask application."""

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "error": "Resource not found",
                "code": "not_found"
            }), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "error": "Internal server error",
                "code": "internal_error"
            }), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "error": "Access forbidden",
                "code": "forbidden"
            }), 403
        return render_template('errors/404.html'), 403

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all other HTTP exceptions."""
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "error": error.description,
                "code": f"http_{error.code}"
            }), error.code
        return render_template('errors/500.html'), error.code

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """Handle all unhandled exceptions."""
        app.logger.error(f'Unhandled exception: {error}')
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                "error": "An unexpected error occurred",
                "code": "unexpected_error"
            }), 500
        return render_template('errors/500.html'), 500
