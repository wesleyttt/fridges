"""
Fridge utilities for managing fridge inventory.

Fridge is represented as:
{
    "item_name": {"quantity": int, "unit_price": float}, ...
}
"""

import logging
from typing import Dict, Any, Optional, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from ..db.dbconnect import get_db_cursor

# Configure logging
logger = logging.getLogger(__name__)


class FridgeManager:
    """Manages fridge operations with proper error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_fridge_by_id(self, uid: Union[str, int]) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Retrieve fridge contents by user ID.
        
        Args:
            uid: User ID (string or integer)
            
        Returns:
            Dictionary of fridge contents or None if not found/error
            Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
        """
        try:
            uid_str = str(uid)
            self.logger.info(f"Retrieving fridge for user: {uid_str}")
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT fridge FROM fridges WHERE uid = %s", 
                    (uid_str,)
                )
                result = cursor.fetchone()
                
                if result:
                    fridge_data = result["fridge"]
                    if fridge_data is None:
                        self.logger.info(f"Empty fridge found for user: {uid_str}")
                        return {}
                    else:
                        self.logger.info(f"Retrieved fridge with {len(fridge_data)} items for user: {uid_str}")
                        return fridge_data
                else:
                    self.logger.warning(f"No fridge found for user: {uid_str}")
                    return None
                    
        except psycopg2.Error as e:
            self.logger.error(f"Database error retrieving fridge for user {uid}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error retrieving fridge for user {uid}: {e}")
            return None
    
    def create_empty_fridge(self, uid: Union[str, int]) -> bool:
        """
        Create an empty fridge for a new user.
        
        Args:
            uid: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            uid_str = str(uid)
            self.logger.info(f"Creating empty fridge for user: {uid_str}")
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO fridges (uid, fridge) VALUES (%s, %s) ON CONFLICT (uid) DO NOTHING",
                    (uid_str, psycopg2.extras.Json({}))
                )
                self.logger.info(f"Empty fridge created for user: {uid_str}")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"Database error creating fridge for user {uid}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating fridge for user {uid}: {e}")
            return False
    
    def update_fridge_contents(self, uid: Union[str, int], fridge_data: Dict[str, Dict[str, Any]]) -> bool:
        """
        Update fridge contents for a user.
        
        Args:
            uid: User ID
            fridge_data: Updated fridge contents
            
        Returns:
            True if successful, False otherwise
        """
        try:
            uid_str = str(uid)
            self.logger.info(f"Updating fridge for user: {uid_str}")
            
            with get_db_cursor() as cursor:
                cursor.execute(
                    "UPDATE fridges SET fridge = %s WHERE uid = %s",
                    (psycopg2.extras.Json(fridge_data), uid_str)
                )
                self.logger.info(f"Fridge updated for user: {uid_str}")
                return True
                
        except psycopg2.Error as e:
            self.logger.error(f"Database error updating fridge for user {uid}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating fridge for user {uid}: {e}")
            return False


# Global fridge manager instance
_fridge_manager: Optional[FridgeManager] = None


def get_fridge_manager() -> FridgeManager:
    """Get the global fridge manager instance."""
    global _fridge_manager
    if _fridge_manager is None:
        _fridge_manager = FridgeManager()
    return _fridge_manager


def get_fridge_by_id(uid: Union[str, int]) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Legacy function for backward compatibility.
    
    Args:
        uid: User ID
        
    Returns:
        Dictionary of fridge contents or None if not found/error
    """
    manager = get_fridge_manager()
    return manager.get_fridge_by_id(uid)

