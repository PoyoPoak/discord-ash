import discord
import openai
import asyncio
import speech_recognition as sr
from gtts import gTTS
from discord.ext import commands
from discord.ext.audiorec import NativeVoiceClient 

bot = commands.Bot(command_prefix = ">",
                      intents=discord.Intents.all())



# PARAMS ----------------------------------------------------------------------



openai.api_key = "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"
discord_bot_key = "MTA3MDI3ODcyNzU4MzQxMjI0NA.G_ly7p.U04jtq-KNc6mCcF1A3jRvT6QPr6_PsYAASlkjU"
model_engine = "text-davinci-003"
server_terminal_ID = 977292010354516039



# EVENTS ----------------------------------------------------------------------



@bot.event
async def on_ready():
    """Bot ready event and sets status.
    """
    await bot.change_presence(status=discord.Status.dnd, 
                                 activity=discord.Game("VSCode"))
    print("We have logged in as {0.user}".format(bot))




# COMMANDS --------------------------------------------------------------------



@bot.event
async def on_message(ctx):
    """Bot message event. Sends message to server terminal.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    channel = ctx.channel
    if channel.id == server_terminal_ID and ctx.author != bot.user:
        response = await prompt_openai(ctx.content)
        print(response)
        await channel.send(response)
    await bot.process_commands(ctx)



@bot.command()
async def test(ctx):
    """Test command.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    await ctx.send("Hello world!")
    
    
    
@bot.command()
async def ping(ctx):
    """Pings the bot and returns latency.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    await ctx.send(f"Pong: {round(bot.latency * 1000)}ms")



@bot.command()
async def join(ctx: commands.Context):
    """Joins the voice channel of the author.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    channel: discord.VoiceChannel = ctx.author.voice.channel
    
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect(cls=NativeVoiceClient)



@bot.command()
async def rec(ctx):    
    """Start recording audio.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    # Start recording.
    ctx.voice_client.record(lambda e: print(f"Exception: {e}"))
    
    # Channel output message.
    embedVar = discord.Embed(title="Started the Recording!",
                             description="use >stop to stop!", 
                             color=0x546e7a)
    await ctx.send(embed=embedVar)



@bot.command()
async def stop(ctx: commands.Context):
    """Stop recording and process audio.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    if not ctx.voice_client.is_recording():
        return

    wav_bytes = await ctx.voice_client.stop_record()

    # Create file and write to file.
    with open(f"prompt.wav", "wb") as f:
        f.write(wav_bytes)
        
    # Channel output message.
    embedVar = discord.Embed(title="Stopped the recording!",
                             color=0x546e7a)
    await ctx.send(embed=embedVar)

    # Process audio and play.
    await process_prompt()
    await play(ctx)



@bot.command() 
async def play(ctx):
    """Plays response.wav audio file in voice channel.

    Args:
        ctx (commands.Context): Standard discord.py context.
    """
    
    # Not sure why, but bot needs to disconnect and reconnect to play audio.
    await ctx.guild.voice_client.disconnect()
    await asyncio.sleep(1)
    
    channel = ctx.author.voice.channel
    
    # Connect to voice channel and play audio.
    if channel is not None:
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio('response.wav'))
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
    else:
        await ctx.channel.send("You are not in a voice channel.")



async def transcribe_audio(audio_file):
    """Transcribes audio file to text.

    Args:
        audio_file (file): Audio file to be transcribed.

    Returns:
        string: Text transcription of audio file.
    """        
    r = sr.Recognizer()

    # Open the file.
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    
    # Transcribe audio with google speech recognition.
    try:
        return r.recognize_google(audio, language='en-US')
    except sr.UnknownValueError:
        return "Error: Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Error: Could not request results from speech recognition service: {e}"
    


async def prompt_openai(prompt):
    """Send prompt to OpenAI and return response.

    Args:
        prompt (string): Text prompt to be sent to OpenAI.

    Returns:
        string: Text response from OpenAI. 
    """
    completion = openai.Completion.create(engine=model_engine,
                                          prompt=prompt,    
                                          max_tokens=1024,    
                                          n=1,
                                          stop=None,
                                          temperature=0.5,)

    response = completion.choices[0].text
    return response


    
async def text_to_speech(text):
    """Takes text and converts to speech. Saves to wav file.

    Args:
        text (string): Text to be converted to speech. 
    """
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("response.wav")
        
        

async def process_prompt():
    """Transcribes audio to text, sends to OpenAI, and converts response to 
        speech.
    """
    transcription = await transcribe_audio("prompt.wav")
    response = await prompt_openai(transcription)
    await text_to_speech(response)



# BEFORE INVOKE ---------------------------------------------------------------



@rec.before_invoke
async def ensure_voice(ctx):
    """Ensure the author is in a voice channel before invoking the command.

    Args:
        ctx (commands.Context): Standard discord.py context.

    Raises:
        commands.CommandError: Errors when user not in voice channel.
    """
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect(cls=NativeVoiceClient)
        else:
            await ctx.send("You are not connected to a voice channel.")
            raise commands.CommandError(
                "Author not connected to a voice channel.")
    elif ctx.voice_client.is_playing():
        ctx.voice_client.stop()

  
        
# START BOT -------------------------------------------------------------------    

bot.run(discord_bot_key)
