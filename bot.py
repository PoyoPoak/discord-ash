import discord
import openai
import json
from discord.ext import commands



# INITIALIZATION --------------------------------------------------------------



# Load config file.
with open("config.json") as f:
    config = json.load(f)

# Clear history file and load initialization prompt.
with open("history.txt", 'w') as f: 
    pass
    if(config["initialize"] == True):  
        f.write(config["initialization_prompt"])

openai.api_key = config["openai_key"]
discord_bot_key = config["bot_key"]
model_engine = config["language_model"]
text_channel = config["text_channel"]

bot = commands.Bot(command_prefix = config["prefix_command"],
                   intents=discord.Intents.all())



# EVENTS ----------------------------------------------------------------------



@bot.event
async def on_ready():
    """Bot ready event and sets status."""
    await bot.change_presence(status=discord.Status.dnd, 
                            activity=discord.Game("VSCode"))
    print("We have logged in as {0.user}".format(bot))



@bot.event
async def on_message(ctx):
    """Bot message event. Sends message response to designated text channel.
    
    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    channel = ctx.channel
    if channel.id == text_channel and ctx.author != bot.user:
        response = await chatgpt(ctx.content, ctx.author.name)
        await channel.send(response)
    await bot.process_commands(ctx)



# FUNCTIONS -------------------------------------------------------------------



async def prompt_openai(prompt, history, author):
    """Prompts OpenAI API for response.

    Args:
        prompt (string): Prompt for AI to respond to.
        history (string): History of conversation for AI to reference.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    input_prompt = history + author + ": " + prompt + "\nAI: "
    print(input_prompt)
    completion = openai.Completion.create(engine="text-davinci-003",
                                          prompt=(input_prompt),  
                                          temperature=0.9,  
                                          max_tokens=1024,    
                                          top_p=1,
                                          frequency_penalty=0,
                                          presence_penalty=0.6,
                                          stop=[" Human:", " AI:"])

    response = completion.choices[0].text.strip()
    return response



async def chatgpt(prompt, author):
    """Calls prompt_openai and writes history to file.

    Args:
        prompt (string): Prompt for AI to respond to.
        author (string): Author of prompt.

    Returns:
        string: Response from AI.
    """
    with open("history.txt", "r") as f:
        history = f.read()
    
    response = await prompt_openai(prompt, history, author)
    
    history += author + ": " + prompt + "\nAI: " + response + "\n"
    
    with open("history.txt", "w") as f:
        f.write(history)
            
    return response
    

        
# START BOT -------------------------------------------------------------------    

bot.run(discord_bot_key)