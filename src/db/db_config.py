import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseConfig:
    """Database configuration using environment variables."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.database = os.getenv('DB_NAME')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.sslmode = os.getenv('DB_SSLMODE', 'require')
        self.channel_binding = os.getenv('DB_CHANNEL_BINDING', 'require')
    
    def get_connection_params(self):
        """Return database connection parameters as a dictionary."""
        return {
            'host': self.host,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'sslmode': self.sslmode,
            'channel_binding': self.channel_binding
        }
    
    def validate(self):
        """Validate that all required environment variables are set."""
        required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create a global instance
db_config = DatabaseConfig()
