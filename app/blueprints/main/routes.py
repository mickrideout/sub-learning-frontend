"""Main application routes."""
import os
import sys
from datetime import datetime, UTC
from flask import jsonify, request

from app.blueprints.main import main_bp


@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint returning system status."""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "python_version": sys.version,
            "system": {
                "platform": sys.platform,
                "hostname": os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            }
        }
        return jsonify(status), 200
    except Exception as e:
        error_response = {
            "error": "Health check failed",
            "code": "health_check_error",
            "timestamp": datetime.now(UTC).isoformat()
        }
        return jsonify(error_response), 500


@main_bp.route('/', methods=['GET'])
def index():
    """Basic index route."""
    return jsonify({
        "message": "Sub Learning Application",
        "status": "running",
        "endpoints": {
            "health": "/health"
        }
    }), 200