"""
Configuration management for the fridges application.

Handles environment variables, configuration validation, and settings.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class Config:
    """Application configuration management."""
    
    def __init__(self):
        """Initialize configuration with environment variables."""
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        # Database configuration
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_sslmode = os.getenv('DB_SSLMODE', 'require')
        self.db_channel_binding = os.getenv('DB_CHANNEL_BINDING', 'require')
        self.db_pool_min_conn = int(os.getenv('DB_POOL_MIN_CONN', '1'))
        self.db_pool_max_conn = int(os.getenv('DB_POOL_MAX_CONN', '10'))
        
        # AI/ML configuration
        self.hf_model_name = os.getenv('HF_MODEL_NAME', 'google/gemma-3-27b-it')
        self.hf_api_token = os.getenv('HF_API_TOKEN')
        
        # Application configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE')
        self.max_image_size = int(os.getenv('MAX_IMAGE_SIZE_MB', '10')) * 1024 * 1024  # Convert to bytes
        
        # File paths
        self.project_root = Path(__file__).parent.parent
        self.prompts_dir = self.project_root / "src" / "cv" / "prompts"
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate required configuration values."""
        required_vars = {
            'DB_HOST': self.db_host,
            'DB_NAME': self.db_name,
            'DB_USER': self.db_user,
            'DB_PASSWORD': self.db_password,
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Validate numeric values
        if self.db_pool_min_conn < 1:
            raise ValueError("DB_POOL_MIN_CONN must be at least 1")
        
        if self.db_pool_max_conn < self.db_pool_min_conn:
            raise ValueError("DB_POOL_MAX_CONN must be greater than or equal to DB_POOL_MIN_CONN")
        
        if self.max_image_size <= 0:
            raise ValueError("MAX_IMAGE_SIZE_MB must be positive")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        logger.info("Configuration validated successfully")
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            'host': self.db_host,
            'database': self.db_name,
            'user': self.db_user,
            'password': self.db_password,
            'sslmode': self.db_sslmode,
            'channel_binding': self.db_channel_binding,
        }
    
    def get_pool_config(self) -> Dict[str, int]:
        """Get connection pool configuration."""
        return {
            'min_conn': self.db_pool_min_conn,
            'max_conn': self.db_pool_max_conn,
        }
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI/ML configuration."""
        config = {
            'model_name': self.hf_model_name,
        }
        
        if self.hf_api_token:
            config['api_token'] = self.hf_api_token
        
        return config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return {
            'level': self.log_level,
            'file': self.log_file,
        }
    
    def get_file_config(self) -> Dict[str, Any]:
        """Get file handling configuration."""
        return {
            'max_image_size': self.max_image_size,
            'prompts_dir': self.prompts_dir,
        }
    
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global _config
    _config = Config()
    return _config
