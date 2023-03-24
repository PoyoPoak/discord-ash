import json
import re
import datetime

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
        
def get_time():
    timestamp = datetime.datetime.now()
    timestamp_string = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
    return timestamp_string

def prune_prefix(input_str):
    pattern1 = r'^assistant: \d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2} Ash: '
    pattern2 = r'^assistant: \d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
    first = re.sub(pattern1, '', input_str)
    second = re.sub(pattern2, '', first)
    return second