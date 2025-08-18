"""Database utility functions for connection testing and optimization."""
import sqlite3
import logging
from contextlib import contextmanager
from typing import Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db

logger = logging.getLogger(__name__)


def test_database_connection() -> Tuple[bool, Optional[str]]:
    """
    Test database connectivity.

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        with db.engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        logger.info("Database connection test successful")
        return True, None
    except Exception as e:
        error_msg = f"Database connection test failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def get_database_info() -> Dict[str, Any]:
    """
    Get comprehensive database information.

    Returns:
        Dictionary containing database metadata
    """
    try:
        info = {
            "engine_type": str(db.engine.url).split('://')[0],
            "database_path": None,
            "tables": [],
            "connection_status": "unknown"
        }

        # Test connection
        connection_ok, error_msg = test_database_connection()
        info["connection_status"] = "connected" if connection_ok else "disconnected"

        if error_msg:
            info["connection_error"] = error_msg
            return info

        # Get database path for SQLite
        if info["engine_type"] == "sqlite":
            db_uri = str(db.engine.url)
            if db_uri.startswith('sqlite:///'):
                info["database_path"] = db_uri[10:]  # Remove 'sqlite:///' prefix

        # Get table information
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        table_info = []
        for table_name in tables:
            try:
                with db.engine.connect() as conn:
                    count_result = conn.execute(
                        text(f'SELECT COUNT(*) FROM {table_name}')).fetchone()
                    row_count = count_result[0] if count_result else 0

                table_info.append({
                    "name": table_name,
                    "row_count": row_count,
                    "columns": [col['name'] for col in inspector.get_columns(table_name)]
                })
            except Exception as e:
                table_info.append({
                    "name": table_name,
                    "error": str(e),
                    "row_count": None,
                    "columns": []
                })

        info["tables"] = table_info

        return info

    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "engine_type": "unknown",
            "connection_status": "error",
            "error": str(e)
        }


def apply_sqlite_optimizations(db_path: str) -> Dict[str, Any]:
    """
    Apply SQLite optimization settings.

    Args:
        db_path: Path to the SQLite database file

    Returns:
        Dictionary with optimization results
    """
    if not db_path:
        return {"error": "Database path not provided"}

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Optimization settings from architecture requirements
        optimizations = [
            ("journal_mode", "WAL"),
            ("synchronous", "NORMAL"),
            ("cache_size", "10000"),
            ("temp_store", "memory"),
            ("mmap_size", "268435456")  # 256MB
        ]

        results = {}

        for setting, value in optimizations:
            try:
                pragma_cmd = f"PRAGMA {setting} = {value};"
                cursor.execute(pragma_cmd)

                # Get the current value to verify
                cursor.execute(f"PRAGMA {setting};")
                current_value = cursor.fetchone()

                results[setting] = {
                    "applied": value,
                    "current": current_value[0] if current_value else None,
                    "success": True
                }

            except Exception as e:
                results[setting] = {
                    "applied": value,
                    "error": str(e),
                    "success": False
                }

        conn.commit()
        conn.close()

        logger.info("SQLite optimizations applied successfully")
        return {"status": "success", "optimizations": results}

    except Exception as e:
        error_msg = f"Failed to apply SQLite optimizations: {e}"
        logger.error(error_msg)
        return {"status": "error", "error": error_msg}


@contextmanager
def database_transaction():
    """
    Context manager for database transactions with automatic rollback on error.

    Usage:
        with database_transaction():
            # Database operations here
            db.session.add(user)
            # Automatically commits on success, rolls back on exception
    """
    try:
        yield db.session
        db.session.commit()
        logger.debug("Database transaction committed successfully")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise


def safe_execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
    """
    Safely execute a database query with error handling.

    Args:
        query: SQL query string
        params: Optional dictionary of query parameters

    Returns:
        Tuple of (success: bool, result: Any)
        If success is False, result contains the error message
    """
    try:
        with db.engine.connect() as conn:
            if params:
                result = conn.execute(text(query), params)
            else:
                result = conn.execute(text(query))

            # Fetch results if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                return True, rows
            else:
                return True, result.rowcount

    except SQLAlchemyError as e:
        error_msg = f"Database query failed: {str(e)}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error executing query: {str(e)}"
        logger.error(error_msg)
        return False, error_msg


def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.

    Args:
        table_name: Name of the table to check

    Returns:
        True if table exists, False otherwise
    """
    try:
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        logger.error(f"Failed to check if table '{table_name}' exists: {e}")
        return False


def get_table_row_count(table_name: str) -> Optional[int]:
    """
    Get the number of rows in a table.

    Args:
        table_name: Name of the table

    Returns:
        Number of rows, or None if error occurred
    """
    if not check_table_exists(table_name):
        logger.warning(f"Table '{table_name}' does not exist")
        return None

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(f'SELECT COUNT(*) FROM {table_name}')).fetchone()
            return result[0] if result else 0
    except Exception as e:
        logger.error(f"Failed to get row count for table '{table_name}': {e}")
        return None
