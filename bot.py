import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
from discord.ext.audiorec import NativeVoiceClient 
import random

bot = commands.Bot(command_prefix = ">",
                      intents=discord.Intents.all())

# ServerTerminal = bot.get_channel(977292010354516039) 

# PARAMS ----------------------------------------------------------------------



# EVENTS ----------------------------------------------------------------------

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, 
                                 activity=discord.Game("VSCode"))
    print("We have logged in as {0.user}".format(bot))


# COMMANDS --------------------------------------------------------------------

@bot.command()
async def ping(ctx):
    await ctx.send(f"Bot latency: {round(bot.latency * 1000)}ms")

# @bot.command(pass_context=True)
# async def join(ctx):
#     if(ctx.author.voice):
#         channel = ctx.message.author.voice.channel
#         await channel.connect()
#     else:
#         await ctx.send("You are not in a voice channel I can join.")

@bot.command()
async def join(ctx: commands.Context):
    channel: discord.VoiceChannel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect(cls=NativeVoiceClient)
    await ctx.invoke(bot.get_command('rec'))

@bot.command()
async def test(ctx):
    await ctx.send('hello im alive!')

@bot.command()
async def rec(ctx):
    ctx.voice_client.record(lambda e: print(f"Exception: {e}"))
    embedVar = discord.Embed(title="Started the Recording!",
                             description="use >stop to stop!", color=0x546e7a)
    await ctx.send(embed=embedVar)

@bot.command()
async def stop(ctx: commands.Context):
    if not ctx.voice_client.is_recording():
        return
    await ctx.send(f'Stopping the Recording')

    wav_bytes = await ctx.voice_client.stop_record()

    name = str(random.randint(000000, 999999))
    with open(f'{name}.wav', 'wb') as f:
        f.write(wav_bytes)
    await ctx.voice_client.disconnect()

@rec.before_invoke
async def ensure_voice(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect(cls=NativeVoiceClient)
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError(
                "Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

        
        
bot.run("MTA3MDI3ODcyNzU4MzQxMjI0NA.G_ly7p.U04jtq-KNc6mCcF1A3jRvT6QPr6_PsYAASlkjU")
