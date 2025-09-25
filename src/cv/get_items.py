"""
Computer vision module for receipt scanning and item extraction.

Given a receipt image, return a list of items and their quantities.
"""

import logging
import base64
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union
from huggingface_hub import InferenceClient
from huggingface_hub.utils import HfHubHTTPError

# Configure logging
logger = logging.getLogger(__name__)


class ReceiptScannerError(Exception):
    """Custom exception for receipt scanning operations."""
    pass


class ReceiptScanner:
    """Handles receipt scanning and item extraction with proper error handling."""
    
    def __init__(self, model_name: str = "google/gemma-3-27b-it"):
        """
        Initialize the receipt scanner.
        
        Args:
            model_name: Hugging Face model name to use for inference
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Hugging Face inference client."""
        try:
            self.client = InferenceClient()
            self.logger.info(f"Initialized Hugging Face client with model: {self.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Hugging Face client: {e}")
            raise ReceiptScannerError(f"Failed to initialize AI client: {e}")
    
    def load_prompt(self) -> str:
        """
        Load the prompt template from file.
        
        Returns:
            Prompt template string
            
        Raises:
            ReceiptScannerError: If prompt file cannot be loaded
        """
        try:
            script_dir = Path(__file__).parent
            prompt_path = script_dir / "prompts" / "extract_info.txt"
            
            if not prompt_path.exists():
                raise ReceiptScannerError(f"Prompt file not found: {prompt_path}")
            
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt_content = f.read().strip()
            
            if not prompt_content:
                raise ReceiptScannerError("Prompt file is empty")
            
            self.logger.debug(f"Loaded prompt template from {prompt_path}")
            return prompt_content
            
        except Exception as e:
            self.logger.error(f"Failed to load prompt template: {e}")
            raise ReceiptScannerError(f"Failed to load prompt template: {e}")
    
    def validate_image_path(self, image_path: Union[str, Path]) -> Path:
        """
        Validate and normalize image path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Normalized Path object
            
        Raises:
            ReceiptScannerError: If image path is invalid
        """
        try:
            path = Path(image_path)
            
            if not path.exists():
                raise ReceiptScannerError(f"Image file does not exist: {path}")
            
            if not path.is_file():
                raise ReceiptScannerError(f"Path is not a file: {path}")
            
            # Check file size (max 10MB)
            file_size = path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10MB
            if file_size > max_size:
                raise ReceiptScannerError(f"Image file too large: {file_size} bytes (max: {max_size})")
            
            # Check file extension
            valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            if path.suffix.lower() not in valid_extensions:
                raise ReceiptScannerError(f"Unsupported image format: {path.suffix}")
            
            return path
            
        except Exception as e:
            if isinstance(e, ReceiptScannerError):
                raise
            self.logger.error(f"Failed to validate image path {image_path}: {e}")
            raise ReceiptScannerError(f"Invalid image path: {e}")
    
    def encode_image(self, image_path: Path) -> str:
        """
        Encode image to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ReceiptScannerError: If image encoding fails
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            self.logger.debug(f"Successfully encoded image: {image_path}")
            return image_data
            
        except Exception as e:
            self.logger.error(f"Failed to encode image {image_path}: {e}")
            raise ReceiptScannerError(f"Failed to encode image: {e}")
    
    def parse_response(self, response: str) -> Dict[str, Dict[str, Any]]:
        """
        Parse AI response and extract items.
        
        Args:
            response: Raw response from AI model
            
        Returns:
            Dictionary of items with quantities and prices
            
        Raises:
            ReceiptScannerError: If response parsing fails
        """
        try:
            # Try to parse as JSON first
            try:
                items = json.loads(response)
                if not isinstance(items, dict):
                    raise ValueError("Response is not a dictionary")
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, try to extract JSON from text
                self.logger.warning("Response is not valid JSON, attempting to extract JSON from text")
                
                # Look for JSON-like content in the response
                start_idx = response.find('{')
                end_idx = response.rfind('}')
                
                if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
                    raise ValueError("No JSON object found in response")
                
                json_str = response[start_idx:end_idx + 1]
                items = json.loads(json_str)
            
            # Validate the structure
            if not isinstance(items, dict):
                raise ValueError("Parsed response is not a dictionary")
            
            # Validate each item
            for item_name, item_data in items.items():
                if not isinstance(item_data, dict):
                    raise ValueError(f"Item data for '{item_name}' is not a dictionary")
                
                required_keys = {"quantity", "unit_price"}
                if not required_keys.issubset(item_data.keys()):
                    missing_keys = required_keys - set(item_data.keys())
                    raise ValueError(f"Item '{item_name}' missing required keys: {missing_keys}")
                
                # Validate numeric values
                try:
                    float(item_data["quantity"])
                    float(item_data["unit_price"])
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Invalid numeric values for item '{item_name}': {e}")
            
            self.logger.info(f"Successfully parsed {len(items)} items from receipt")
            return items
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI response: {e}")
            self.logger.debug(f"Raw response: {response}")
            raise ReceiptScannerError(f"Failed to parse AI response: {e}")
    
    def scan_receipt(self, image_path: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
        """
        Scan a receipt image and extract items with quantities and prices.
        
        Args:
            image_path: Path to the receipt image
            
        Returns:
            Dictionary of items with quantities and prices
            Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
            
        Raises:
            ReceiptScannerError: If scanning fails
        """
        try:
            # Validate image path
            validated_path = self.validate_image_path(image_path)
            self.logger.info(f"Starting receipt scan for image: {validated_path}")
            
            # Load prompt template
            prompt_template = self.load_prompt()
            
            # Encode image
            image_data = self.encode_image(validated_path)
            
            # Create the message with image and prompt
            self.logger.debug("Sending request to AI model")
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_template
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
            )
            
            if not completion.choices or not completion.choices[0].message.content:
                raise ReceiptScannerError("Empty response from AI model")
            
            response = completion.choices[0].message.content
            self.logger.debug(f"Received response from AI model: {len(response)} characters")
            
            # Parse and validate response
            items = self.parse_response(response)
            
            self.logger.info(f"Successfully scanned receipt with {len(items)} items")
            return items
            
        except HfHubHTTPError as e:
            self.logger.error(f"Hugging Face API error: {e}")
            raise ReceiptScannerError(f"AI service error: {e}")
        except Exception as e:
            if isinstance(e, ReceiptScannerError):
                raise
            self.logger.error(f"Unexpected error scanning receipt {image_path}: {e}")
            raise ReceiptScannerError(f"Failed to scan receipt: {e}")


# Global receipt scanner instance
_receipt_scanner: Optional[ReceiptScanner] = None


def get_receipt_scanner() -> ReceiptScanner:
    """Get the global receipt scanner instance."""
    global _receipt_scanner
    if _receipt_scanner is None:
        _receipt_scanner = ReceiptScanner()
    return _receipt_scanner


def scan_receipt(image_path: Union[str, Path]) -> Dict[str, Dict[str, Any]]:
    """
    Legacy function for backward compatibility.
    
    Scan a receipt image and extract items with quantities and prices.
    
    Args:
        image_path: Path to the receipt image
        
    Returns:
        Dictionary of items with quantities and prices
        Format: {"item_name": {"quantity": int, "unit_price": float}, ...}
    """
    scanner = get_receipt_scanner()
    return scanner.scan_receipt(image_path)    