import json

def load_config():
    """Loads config file.

    Returns:
        dict: Config file.
    """
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
        
    return config

def read_json():
    """Reads history array from file.

    Returns:
        array: Array from file.
    """
    with open("history.json", 'r') as f:
        array = json.load(f)
        
    return array

def write_json(array):
    """Writes array to file.

    Args:
        array (array): Array to write to file.
    """
    with open("history.json", 'w') as outfile:
        json.dump(array, outfile)
        
def wipe_json():
    """Wipes history json."""
    with open("history.json", 'w') as f:
        json.dump([], f)
        
def initialize_json(prompt):
    """Initializes history json. Adds initial prompt."""
    with open("history.json", 'w') as f:
        json.dump([{
            "role": "system", 
            "content": prompt}], f)