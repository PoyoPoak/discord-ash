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
        json.dump([], f)

# API Keys.
openai.api_key = config["openai_key"]
discord_bot_key = config["bot_key"]

model_engine = config["language_models"]["chat"]

text_channel = config["text_channels"]["server_terminal"]

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



async def gpt_turbo(prompt, history):
    """Prompts OpenAI API for response.

    Args:
        prompt (string): Prompt for AI to respond to.
        history (string): History of conversation for AI to reference.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    history.append({'role': 'user', 'content': prompt})
    
    # Constructs prompt for OpenAI API input.
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history)

    return completion.choices[0].text.strip()



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
            
    elif(model_engine == "gpt-3.5-turbo"):
        history = read_array_from_file()
        history.append({"role": "system", "content": config["initialization_prompt"]})
        history = gpt_turbo(prompt, history)
        response = '{0}: {1}\n'.format(history[-1]['role'].strip(), 
                                       history[-1]['content'].strip())
            
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



def read_array_from_file():
    """Reads array from file.

    Returns:
        array: Array from file.
    """
    with open("history.json", 'r') as f:
        array = json.load(f)
    return array


       
def write_array_to_file(array):
    """Writes array to file.

    Args:
        array (array): Array to write to file.
    """
    with open("history.json", 'w') as f:
        for item in array:
            f.write(f"role: {item['role']}\n")
            f.write(f"content: {item['content']}\n\n")
       
     
     
# START BOT -------------------------------------------------------------------    

bot.run(discord_bot_key)