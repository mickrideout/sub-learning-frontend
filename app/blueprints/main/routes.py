"""Main application routes."""
import os
import sys
from datetime import datetime, UTC
from flask import jsonify
from sqlalchemy import text

from app.blueprints.main import main_bp
from app import db


def get_database_status():
    """Get database connection status and metadata."""
    try:
        # Test basic connectivity
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1')).fetchone()

        # Check if users table exists
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        users_table_exists = 'users' in tables

        # Get user count if table exists
        user_count = 0
        if users_table_exists:
            with db.engine.connect() as conn:
                count_result = conn.execute(text('SELECT COUNT(*) FROM users')).fetchone()
                user_count = count_result[0] if count_result else 0

        return {
            "status": "connected",
            "tables": {
                "users": {
                    "exists": users_table_exists,
                    "count": user_count if users_table_exists else None
                }
            },
            "engine": str(db.engine.url).split('://')[0],  # sqlite, postgresql, etc.
            "total_tables": len(tables)
        }, True

    except Exception as e:
        return {
            "status": "disconnected",
            "error": str(e),
            "code": "database_connection_error"
        }, False


@main_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint returning system status."""
    try:
        # Get database status
        db_status, db_healthy = get_database_status()

        overall_status = "healthy" if db_healthy else "unhealthy"

        status = {
            "status": overall_status,
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
            "environment": os.environ.get('FLASK_ENV', 'development'),
            "python_version": sys.version,
            "system": {
                "platform": sys.platform,
                "hostname": os.uname().nodename if hasattr(os, 'uname') else 'unknown'
            },
            "database": db_status
        }

        status_code = 200 if db_healthy else 503
        return jsonify(status), status_code

    except Exception:
        error_response = {
            "error": "Health check failed",
            "code": "health_check_error",
            "timestamp": datetime.now(UTC).isoformat()
        }
        return jsonify(error_response), 500


@main_bp.route('/health/database', methods=['GET'])
def database_health_check():
    """Dedicated database health check endpoint."""
    try:
        db_status, db_healthy = get_database_status()
        db_status["timestamp"] = datetime.now(UTC).isoformat()

        status_code = 200 if db_healthy else 503
        return jsonify(db_status), status_code

    except Exception:
        error_response = {
            "status": "error",
            "error": "Database health check failed",
            "code": "database_health_error",
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
            "health": "/health",
            "database_health": "/health/database"
        }
    }), 200
