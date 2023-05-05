import discord
import openai
from discord.ext import commands
from functions import *
from chat import *

# Load config file.
config = load_config()

# Grabbing config values
openai.api_key = config["openai_key"]
discord_bot_key = config["bot_key"]
model_engine = config["model"]
text_channel = config["text_channel"]
initialization_prompt = config["initialization_prompt"]
clean_slate = config["clean_slate"]
inactivity_period = config["inactivity_period"]

last_interaction = datetime.datetime.now()

bot = commands.Bot(command_prefix = config["prefix_command"],
                   intents=discord.Intents.all())

if(clean_slate):
    wipe_json()
    initialize_json(initialization_prompt)

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
        response = await chatgpt(ctx.content, ctx.author.name, model_engine)
        # Send response to designated text channel.
        await channel.send(response)

    # Check if bot has been inactive for a certain amount of time.
    global last_interaction
    now = datetime.datetime.now()
    time_since_last_interaction = (now - last_interaction).total_seconds()
    
    # If bot has been inactive for a certain amount of time, condense memory.
    if time_since_last_interaction > inactivity_period:
        await condense_memory()
        
    # Update last interaction time.
    last_interaction = now

    await bot.process_commands(ctx)
    
async def condense_memory():
    """Condenses memory by summarizing conversation history and wiping memory.
    """
    # Summarize conversation history and write it to file.
    summary = await davincii_combine()
    write_txt("old_summary.txt", summary)
    
    # Reset history with summary.
    wipe_json()
    initialize_json(initialization_prompt + 
                    " Here is a summary of your conversations so far: " + 
                    summary)

bot.run(discord_bot_key)