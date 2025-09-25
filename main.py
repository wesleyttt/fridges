#!/usr/bin/env python3
"""
Fridges - Smart Fridge Management System

Main entry point for the fridges application.
Provides CLI interface for receipt scanning and fridge management.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cv import scan_receipt, ReceiptScanner
from src.fridge import update_fridge, get_fridge_by_id, FridgeUpdater
from src.db import get_db_manager


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def scan_and_update_fridge(image_path: str, user_id: str, dry_run: bool = False) -> bool:
    """
    Scan a receipt and update fridge inventory.
    
    Args:
        image_path: Path to receipt image
        user_id: User ID for fridge
        dry_run: If True, don't actually update the database
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🔍 Scanning receipt: {image_path}")
        
        # Scan receipt
        items = scan_receipt(image_path)
        print(f"✅ Found {len(items)} items in receipt")
        
        # Display items
        print("\n📋 Receipt items:")
        for item_name, item_data in items.items():
            print(f"  • {item_name}: {item_data['quantity']} @ ${item_data['unit_price']:.2f}")
        
        if dry_run:
            print("\n🔍 DRY RUN - No database changes made")
            return True
        
        # Update fridge
        print(f"\n📦 Updating fridge for user: {user_id}")
        success, message = update_fridge(user_id, items)
        
        if success:
            print(f"✅ {message}")
            return True
        else:
            print(f"❌ {message}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_fridge_contents(user_id: str) -> bool:
    """
    Display current fridge contents.
    
    Args:
        user_id: User ID for fridge
        
    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📦 Fridge contents for user: {user_id}")
        
        fridge_contents = get_fridge_by_id(user_id)
        
        if fridge_contents is None:
            print("❌ No fridge found for this user")
            return False
        elif not fridge_contents:
            print("📭 Fridge is empty")
            return True
        
        print(f"\n📋 Fridge contains {len(fridge_contents)} items:")
        total_value = 0
        
        for item_name, item_data in fridge_contents.items():
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            total_price = quantity * unit_price
            total_value += total_price
            
            print(f"  • {item_name}: {quantity} @ ${unit_price:.2f} (${total_price:.2f})")
        
        print(f"\n💰 Total fridge value: ${total_value:.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Smart Fridge Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan receipt and update fridge
  python main.py scan receipt.jpg --user-id user123
  
  # Dry run (scan but don't update database)
  python main.py scan receipt.jpg --user-id user123 --dry-run
  
  # View fridge contents
  python main.py fridge user123
  
  # Enable debug logging
  python main.py scan receipt.jpg --user-id user123 --log-level DEBUG
        """
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Log to file instead of console"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan receipt and update fridge")
    scan_parser.add_argument("image_path", help="Path to receipt image")
    scan_parser.add_argument("--user-id", required=True, help="User ID for fridge")
    scan_parser.add_argument("--dry-run", action="store_true", help="Don't update database")
    
    # Fridge command
    fridge_parser = subparsers.add_parser("fridge", help="View fridge contents")
    fridge_parser.add_argument("user_id", help="User ID for fridge")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level, args.log_file)
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == "scan":
            success = scan_and_update_fridge(
                args.image_path, 
                args.user_id, 
                args.dry_run
            )
            return 0 if success else 1
            
        elif args.command == "fridge":
            success = show_fridge_contents(args.user_id)
            return 0 if success else 1
            
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())