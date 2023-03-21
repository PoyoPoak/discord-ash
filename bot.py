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

    await bot.process_commands(ctx)

bot.run(discord_bot_key)