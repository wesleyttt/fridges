"""
Core source package for fridges application.
"""

from .db import get_db_connection
from .fridge import update_fridge, get_fridge_by_id
from .cv import scan_receipt

__all__ = [
    "get_db_connection",
    "update_fridge", 
    "get_fridge_by_id",
    "scan_receipt"
]
