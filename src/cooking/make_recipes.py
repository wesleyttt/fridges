"""
Given a list of items and their quantities, make a recipe.
"""
import os
import json
from transformers import AutoTokenizer, BartForConditionalGeneration

def load_prompt():
    """Load the prompt template from file."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = os.path.join(script_dir, "prompts", "generate_recipes.txt")
    
    with open(prompt_path, "r") as f:
        return f.read().strip()

def make_recipes(uid, items):
    # items = get_fridge_by_id(uid)
    # if not items:
    #     return None
    
    # Convert list of items to a dictionary for the prompt
    items_dict = {item: {"quantity": items[item]["quantity"]} for item in items}
    
    # Convert items into a JSON string
    items_string = json.dumps(items_dict, indent=2)

    # Create LLM prompt
    prompt = load_prompt().format(items_string=items_string)
    
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")

    inputs = tokenizer([prompt], return_tensors="pt", max_length=1024)
    
    # Call Huggingface LLM API
    summary_ids = model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=1024)
    recipe_text = tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    
    # Parse response
    return recipe_text
    