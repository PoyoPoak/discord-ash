import openai
import re
from functions import *

def filter_ascii(user_input):
    """ Removes emojis and non-ascii characters from user input.

    Args:
        user_input (string): User input.

    Returns:
        string: Filtered user input.
    """
    # Discord emoji handling.
    user_input = re.sub(r"<:\w+:\d+>", "", user_input)
    
    # Filter for non ascii chars.
    user_input = ''.join([char for char in user_input if ord(char) < 128])
    
    return user_input

async def prompt_model(prompt, history, author):
    """Prompts OpenAI API for response.

    Args:
        prompt (string): Prompt for AI to respond to.
        history (string): History of conversation for AI to reference.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    # Assembles history array with prompt for OpenAI API input.
    history.append({'role': 'user', 'content': author + ": " + prompt})
    
    # Get response from OpenAI API.
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history)

    # Append history with prompt and response.
    history.append({
        'role': completion.choices[0].message.role, 
        'content': completion.choices[0].message.content})
    
    return history

async def chatgpt(prompt, author, model_engine):
    """Calls OpenAI API and writes history to file.

    Args:
        prompt (string): Prompt for AI to respond to.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    # Filter user input and removes invalid characters.
    prompt = filter_ascii(prompt)
    
    if(model_engine == "gpt-3.5-turbo"):
        # Read history from file.
        history = read_json()
        
        # Gets response from OpenAI API given prompt, history, and author.
        history = await prompt_model(prompt, history, author)
        
        write_json(history)
        
        # Output response array.
        response = '{0}: {1}\n'.format(
            history[-1]['role'].strip(), 
            history[-1]['content'].strip())
        
        # Trim the "assistant: Ash: " part of the response.
        if response.startswith("assistant: Ash: "):
            response = response[16:]
        elif (response.startswith("assistant: Ash: ")):
            response = response
        
    return response