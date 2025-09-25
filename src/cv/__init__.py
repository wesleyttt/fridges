"""
Computer vision package for receipt scanning.
"""

from .get_items import scan_receipt, ReceiptScanner

__all__ = [
    "scan_receipt",
    "ReceiptScanner"
]
