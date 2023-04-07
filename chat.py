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
    time_Stamp = get_time()
    
    # Assembles history array with prompt for OpenAI API input.
    history.append({'role': 'user', 'content': time_Stamp + " " + author + ": " + prompt})
    
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
        
        # Trim the prefixes of part of the response.
        response = prune_prefix(response)
        
    return response

async def davincii_summarize():
    """Summarizes chat history using OpenAI API.

    Returns:
        string: Summary of chat history.
    """
    prompt = "Summarize the events and topics of the following chat log: "
        
    # Get condensed chat log.
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

async def davincii_combine():
    """Combines two summaries using OpenAI API.

    Returns:
        string: Combined summaries of chat history.
    """
    prompt = "Combine the two summaries and shorten them. The first summary "\
	"summarizes the events of older conversations. The second summary "\
        "summarizes the events of the most recent conversation. Combine the "\
        "two summaries into a single summary. Ensure all events and topics "\
        "are kept. \nHere is the first summary: \n"
        
    # Get current sumamry and condensed chat log.
    old_history = read_txt("old_summary.txt")
    new_history = await davincii_summarize()
        
    # Constructs prompt for OpenAI API input.
    input_prompt =  (prompt + 
                     old_history + 
                     "\nHere is the second summary: \n" + 
                     new_history)
    
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