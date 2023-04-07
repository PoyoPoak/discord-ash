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
        
def read_txt(file_path):
    """Reads contents to string from file.

    Returns:
        string: String from file.
    """
    with open(file_path, 'r') as f:
        string = f.read()
        
    return string

def write_txt(file_path, string):
    """Writes string to file.

    Args:
        file_path (string): Path to file.
        string (string): String to write to file.
    """
    with open(file_path, 'w') as f:
        f.write(string)
        
def get_time():
    """Gets current time.

    Returns:
        string: Current time. 
    """
    today = datetime.datetime.now()
    return today.strftime("%a %b %d %H:%M:%S %Y")

def prune_prefix(input_str):
    """Removes prefix from input string.

    Args:
        input_str (string): Input string.

    Returns:
        string: Input string without prefix. 
    """
    pat_assist = r'^assistant: '
    pat_name = r'^Ash: ' 
    rem_assist = re.sub(pat_assist, '', input_str)
    rem_name = re.sub(pat_name, '', rem_assist)
    return rem_name

def get_condensed_history():
    """Condenses history into one string.

    Returns:
        strin: Condensed history string.
    """
    with open("history.json", 'r') as f:
        data = json.load(f)
        contents = ''
        for index, item in enumerate(data):
            if index > 0:
                contents += item['content'] + ' '
        return contents.strip()