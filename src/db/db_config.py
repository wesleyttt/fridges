"""
Database configuration using the centralized config system.

This module provides backward compatibility for the old DatabaseConfig class.
"""

from ..config import get_config


class DatabaseConfig:
    """Database configuration using the centralized config system."""
    
    def __init__(self):
        """Initialize with centralized configuration."""
        self.config = get_config()
    
    def get_connection_params(self):
        """Return database connection parameters as a dictionary."""
        return self.config.get_database_config()
    
    def validate(self):
        """Validate that all required environment variables are set."""
        # Configuration validation is handled in the Config class
        return True


# Create a global instance for backward compatibility
db_config = DatabaseConfig()


