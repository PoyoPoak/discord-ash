import discord
import openai
import json
import re
from discord.ext import commands



# INITIALIZATION --------------------------------------------------------------



# Load config file.
with open("config.json") as f:
    config = json.load(f)

# Clear history txt and load initialization prompt.
with open("history.txt", 'w') as f: 
    pass
    if(config["initialize"] == True):  
        f.write(config["initialization_prompt"])
        
# Clear history json file.
with open("history.json", 'w') as f:
    if(config["initialize"] == True):
        json.dump([{
            "role": "system", 
            "content": config["initialization_prompt"]}], f)
    elif(config["initialize"] == False):
        json.dump([], f)

# API Keys.
openai.api_key = config["openai_key"]
discord_bot_key = config["bot_key"]

model_engine = config["language_models"]["chat"]

text_channel = config["text_channels"]["lab"]

bot = commands.Bot(command_prefix = config["prefix_command"],
                   intents=discord.Intents.all())



# EVENTS ----------------------------------------------------------------------



@bot.event
async def on_ready():
    """Bot ready event and sets status."""
    await bot.change_presence(
        status=discord.Status.dnd, 
        activity=discord.Game(config["bot_info"]["activity"]))
    print("We have logged in as {0.user}".format(bot))



@bot.event
async def on_message(ctx):
    """Bot message event. Sends message response to designated text channel.
    
    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    # Sets channel to interact with.
    channel = ctx.channel
    
    # If message is in designated text channel and not from bot, send response.
    if channel.id == text_channel and ctx.author != bot.user:
        # Get response from chatgpt function.
        response = await chatgpt(ctx.content, ctx.author.name)
        # Send response to designated text channel.
        await channel.send(response)

    await bot.process_commands(ctx)



# FUNCTIONS -------------------------------------------------------------------



async def prompt_davinci(prompt, history, author):
    """Prompts OpenAI API for response.

    Args:
        prompt (string): Prompt for AI to respond to.
        history (string): History of conversation for AI to reference.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    # Constructs prompt for OpenAI API input.
    input_prompt = history + author + ": " + prompt + "\nAI: "
    
    # Get response from OpenAI API.
    completion = openai.Completion.create(
        engine="text-davinci-003",
        prompt=(input_prompt),  
        temperature=0.9,  
        max_tokens=1024,    
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"])

    return completion.choices[0].text.strip()



async def prompt_turbo(prompt, history, author):
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



async def chatgpt(prompt, author):
    """Calls OpenAI API and writes history to file.

    Args:
        prompt (string): Prompt for AI to respond to.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    # Filter user input and removes invalid characters.
    prompt = filter_ascii(prompt)
    
    # Process for handling text-davinci-003 model.
    if(model_engine == "text-davinci-003"):
        # Read history from file.
        with open("history.txt", "r") as f:
            history = f.read()
            
        # Gets response from OpenAI API given prompt, history, and author.
        response = await prompt_davinci(prompt, history, author)
        
        # Append history with prompt and response.
        history += author + ": " + prompt + "\nAI: " + response + "\n"
        
        # Write history to file.
        with open("history.txt", "w") as f:
            f.write(history)
            
    # Process for handling gpt-3.5-turbo model.
    elif(model_engine == "gpt-3.5-turbo"):
        # Read history from file.
        history = read_json()
        
        # Gets response from OpenAI API given prompt, history, and author.
        history = await prompt_turbo(prompt, history, author)
        
        write_json(history)
        
        # Output response array.
        response = '{0}: {1}\n'.format(
            history[-1]['role'].strip(), 
            history[-1]['content'].strip())
        
        # Trim the "assistant: Ash: " part of the response.
        response = response[15:]
        
    return response
    


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



def initialize_json():
    """Initializes history json. Wipes and adds initial prompt."""
    with open("history.json", 'w') as f:
        if(config["initialize"] == True):
            json.dump([{
                "role": "system", 
                "content": config["initialization_prompt"]}], f)
        elif(config["initialize"] == False):
            json.dump([], f)     



def initialize_txt():
    """Initializes history txt. Wipes and adds initial prompt."""
    with open("history.txt", 'w') as f: 
        pass
        if(config["initialize"] == True):  
            f.write(config["initialization_prompt"])



# START BOT -------------------------------------------------------------------    

bot.run(discord_bot_key)