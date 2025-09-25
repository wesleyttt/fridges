"""
Fridge update operations with proper error handling and validation.

Given a scan of a receipt, update the fridge with the items and quantities.
"""

import logging
from typing import Dict, Any, Union, Tuple, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from ..db.dbconnect import get_db_cursor
from ..cv.get_items import scan_receipt
from .fridge_utils import get_fridge_manager, FridgeManager

# Configure logging
logger = logging.getLogger(__name__)


class FridgeUpdateError(Exception):
    """Custom exception for fridge update operations."""
    pass


class FridgeUpdater:
    """Handles fridge update operations with proper validation and error handling."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fridge_manager = get_fridge_manager()
    
    def validate_items(self, items: Dict[str, Dict[str, Any]]) -> None:
        """
        Validate items dictionary structure.
        
        Args:
            items: Dictionary of items to validate
                Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
                
        Raises:
            FridgeUpdateError: If validation fails
        """
        if not isinstance(items, dict):
            raise FridgeUpdateError("Items must be a dictionary")
        
        if not items:
            raise FridgeUpdateError("Items dictionary cannot be empty")
        
        for item_name, item_data in items.items():
            if not isinstance(item_name, str) or not item_name.strip():
                raise FridgeUpdateError(f"Invalid item name: '{item_name}'")
            
            if not isinstance(item_data, dict):
                raise FridgeUpdateError(f"Item data for '{item_name}' must be a dictionary")
            
            required_keys = {"quantity", "unit_price"}
            if not required_keys.issubset(item_data.keys()):
                missing_keys = required_keys - set(item_data.keys())
                raise FridgeUpdateError(f"Item '{item_name}' missing required keys: {missing_keys}")
            
            try:
                quantity = float(item_data["quantity"])
                unit_price = float(item_data["unit_price"])
                
                if quantity <= 0:
                    raise FridgeUpdateError(f"Quantity for '{item_name}' must be positive")
                if unit_price < 0:
                    raise FridgeUpdateError(f"Unit price for '{item_name}' cannot be negative")
                    
            except (ValueError, TypeError) as e:
                raise FridgeUpdateError(f"Invalid numeric values for item '{item_name}': {e}")
    
    def calculate_weighted_average_price(self, existing_item: Dict[str, Any], new_item: Dict[str, Any]) -> float:
        """
        Calculate weighted average price for an item.
        
        Args:
            existing_item: Current item data
            new_item: New item data
            
        Returns:
            Weighted average unit price (rounded to 2 decimal places)
        """
        existing_qty = existing_item["quantity"]
        existing_price = existing_item["unit_price"]
        new_qty = new_item["quantity"]
        new_price = new_item["unit_price"]
        
        total_qty = existing_qty + new_qty
        total_value = (existing_qty * existing_price) + (new_qty * new_price)
        
        # Round to 2 decimal places to avoid floating-point precision issues
        return round(total_value / total_qty, 2)
    
    def merge_items(self, current_fridge: Dict[str, Dict[str, Any]], new_items: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Merge new items into current fridge contents.
        
        Args:
            current_fridge: Current fridge contents
            new_items: New items to add
            
        Returns:
            Updated fridge contents
        """
        updated_fridge = current_fridge.copy()
        
        for item_name, item_data in new_items.items():
            if item_name in updated_fridge:
                # Item exists - update quantity and calculate weighted average price
                updated_fridge[item_name]["quantity"] += item_data["quantity"]
                updated_fridge[item_name]["unit_price"] = self.calculate_weighted_average_price(
                    updated_fridge[item_name], item_data
                )
                self.logger.info(f"Updated existing item '{item_name}': +{item_data['quantity']} units")
            else:
                # New item - add directly with rounded price
                updated_fridge[item_name] = {
                    "quantity": item_data["quantity"],
                    "unit_price": round(float(item_data["unit_price"]), 2)
                }
                self.logger.info(f"Added new item '{item_name}': {item_data['quantity']} units @ ${updated_fridge[item_name]['unit_price']:.2f}")
        
        return updated_fridge
    
    def update_fridge(self, uid: Union[str, int], items: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Add items from receipt to fridge database.
        
        Args:
            uid: User ID
            items: Dictionary of items to add
                Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
                
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate input
            self.validate_items(items)
            uid_str = str(uid)
            
            self.logger.info(f"Starting fridge update for user {uid_str} with {len(items)} items")
            
            # Get current fridge contents
            current_fridge = self.fridge_manager.get_fridge_by_id(uid)
            
            if current_fridge is None:
                # Create empty fridge if user doesn't have one
                self.logger.info(f"No existing fridge found for user {uid_str}, creating new one")
                if not self.fridge_manager.create_empty_fridge(uid):
                    return False, "Failed to create new fridge for user"
                current_fridge = {}
            
            # Merge new items with existing fridge
            updated_fridge = self.merge_items(current_fridge, items)
            
            # Update fridge in database
            if not self.fridge_manager.update_fridge_contents(uid, updated_fridge):
                return False, "Failed to update fridge in database"
            
            self.logger.info(f"Successfully updated fridge for user {uid_str}")
            return True, f"Successfully added {len(items)} items to fridge {uid_str}"
            
        except FridgeUpdateError as e:
            self.logger.error(f"Validation error updating fridge for user {uid}: {e}")
            return False, f"Validation error: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error updating fridge for user {uid}: {e}")
            return False, f"Unexpected error: {e}"


# Global fridge updater instance
_fridge_updater: Optional[FridgeUpdater] = None


def get_fridge_updater() -> FridgeUpdater:
    """Get the global fridge updater instance."""
    global _fridge_updater
    if _fridge_updater is None:
        _fridge_updater = FridgeUpdater()
    return _fridge_updater


def update_fridge(uid: Union[str, int], items: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Legacy function for backward compatibility.
    
    Add items from receipt to fridge database.
    
    Args:
        uid: User ID
        items: Dictionary of items to add
            Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
            
    Returns:
        Tuple of (success: bool, message: str)
    """
    updater = get_fridge_updater()
    return updater.update_fridge(uid, items)
    