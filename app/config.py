"""Application configuration."""
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))


class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Flask configuration
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', 'true').lower() in ['true', '1', 'on']

    # Database configuration
    DATABASE_URL = (os.environ.get('DATABASE_URL') or
                    f'sqlite:///{os.path.join(basedir, "..", "instance", "subtitle_database.db")}')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
