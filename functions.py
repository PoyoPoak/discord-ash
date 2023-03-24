import json
import re
import datetime
import openai

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
    """Gets current time.

    Returns:
        string: Current time. 
    """
    timestamp = datetime.datetime.now()
    timestamp_string = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
    return timestamp_string

def prune_prefix(input_str):
    """Removes prefix from input string.

    Args:
        input_str (string): Input string.

    Returns:
        string: Input string without prefix. 
    """
    pattern1 = r'^assistant: \d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2} Ash: '
    pattern2 = r'^assistant: \d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}'
    first = re.sub(pattern1, '', input_str)
    second = re.sub(pattern2, '', first)
    return second

def get_condensed_history():
    with open("history.json", 'r') as f:
        data = json.load(f)
        contents = ''
        for item in data:
            contents += item['content'] + ' '
        return contents.strip()
    
async def get_summary():
    prompt = "Summarize the following chat log while maintaining dates: "
    condensed = get_condensed_history()
    
    # Constructs prompt for OpenAI API input.
    input_prompt = prompt + condensed
    
    # Get response from OpenAI API.
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(input_prompt),  
        temperature=0.7,  
        max_tokens=1024,    
        top_p=1,
        frequency_penalty=0,
        presence_penalty=1.0)

    return completion.choices[0].text.strip()

async def clean_memory(initial_prompt):
    summary = await get_summary()
    wipe_json()
    wipe_start = initial_prompt + " Here is a summary of your conversations so far: " + summary
    initialize_json(wipe_start)