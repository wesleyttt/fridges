"""
Given a receipt image, return a list of items and their quantities.
"""

from huggingface_hub import InferenceClient
import base64
import json
import os

client = InferenceClient()

def load_prompt():
    """Load the prompt template from file."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, "prompts", "extract_info.txt")
    
    with open(prompt_path, "r") as f:
        return f.read().strip()

def scan_receipt(image_path):
    """
    Input: image_path
    Output: [{item: , quantity:}, ...]
    """
    
    # Load the prompt template
    prompt_template = load_prompt()
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # Create the message with image and prompt
    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it",
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

    response = completion.choices[0].message.content
    
    return response    