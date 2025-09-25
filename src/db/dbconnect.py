"""
Database connection management with proper error handling and context managers.
"""

import logging
from contextlib import contextmanager
from typing import Optional, Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from .db_config import DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections with connection pooling."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Optional[SimpleConnectionPool] = None
    
    def initialize_pool(self, min_conn: int = 1, max_conn: int = 10) -> None:
        """Initialize connection pool."""
        try:
            self.config.validate()
            conn_params = self.config.get_connection_params()
            
            self._pool = SimpleConnectionPool(
                min_conn, max_conn, **conn_params
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    def get_connection(self) -> psycopg2.extensions.connection:
        """Get a connection from the pool."""
        if not self._pool:
            self.initialize_pool()
        
        try:
            return self._pool.getconn()
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            raise
    
    def return_connection(self, conn: psycopg2.extensions.connection) -> None:
        """Return a connection to the pool."""
        if self._pool:
            self._pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator[psycopg2.extras.RealDictCursor, None, None]:
        """Context manager for database cursor with automatic cleanup."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=cursor_factory)
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                self.return_connection(conn)
    
    def close_pool(self) -> None:
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            logger.info("Database connection pool closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        config = DatabaseConfig()
        _db_manager = DatabaseManager(config)
    return _db_manager


def get_db_connection() -> Optional[psycopg2.extensions.connection]:
    """Legacy function for backward compatibility."""
    try:
        manager = get_db_manager()
        return manager.get_connection()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        return None


@contextmanager
def get_db_cursor(cursor_factory=RealDictCursor) -> Generator[psycopg2.extras.RealDictCursor, None, None]:
    """Context manager for database operations."""
    manager = get_db_manager()
    with manager.get_cursor(cursor_factory) as cursor:
        yield cursor

