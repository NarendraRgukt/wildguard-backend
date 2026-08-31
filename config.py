import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://wildguard:wildguard123@localhost:5432/wildguard_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    CORS_ORIGINS = "*"
    
    # GPS Simulator
    GPS_SIMULATOR_INTERVAL = 30  # seconds
    
    # Geofencing
    RAILWAY_BUFFER_M = 1000
    VILLAGE_BUFFER_M = 2000
    
    # Risk thresholds
    RISK_LOW_THRESHOLD = 30
    RISK_MEDIUM_THRESHOLD = 60
    RISK_HIGH_THRESHOLD = 80
    
    # Model paths
    MEGADETECTOR_MODEL_PATH = None  # Will be loaded dynamically
    PYTORCH_WILDLIFE_MODEL_PATH = None  # Will be loaded dynamically

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
