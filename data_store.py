import json
from datetime import datetime
import os

OPINIONS_FILE = "trading_opinions.json"

def save_opinion(opinion):
    """
    Save trading opinion to a JSON file
    """
    try:
        opinions = []
        if os.path.exists(OPINIONS_FILE):
            with open(OPINIONS_FILE, 'r') as f:
                opinions = json.load(f)
        
        # Add accuracy field (to be updated later)
        opinion['accuracy'] = None
        opinions.append(opinion)
        
        # Keep only last 100 opinions
        opinions = opinions[-100:]
        
        with open(OPINIONS_FILE, 'w') as f:
            json.dump(opinions, f)
            
    except Exception as e:
        raise Exception(f"Failed to save opinion: {str(e)}")

def get_historical_opinions():
    """
    Retrieve historical trading opinions
    """
    try:
        if os.path.exists(OPINIONS_FILE):
            with open(OPINIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        raise Exception(f"Failed to retrieve historical opinions: {str(e)}")
