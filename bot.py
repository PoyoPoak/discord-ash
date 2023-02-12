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
model_engine = "text-davinci-003"



# EVENTS ----------------------------------------------------------------------



@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, 
                                 activity=discord.Game("VSCode"))
    print("We have logged in as {0.user}".format(bot))




# COMMANDS --------------------------------------------------------------------



# Prints a hello world to text channel.
@bot.command()
async def test(ctx):
    await ctx.send("Hello world!")
    
    
    
# Print bot's latency to text channel.
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong: {round(bot.latency * 1000)}ms")



# Summons bot to VC of command author.
@bot.command()
async def join(ctx: commands.Context):
    channel: discord.VoiceChannel = ctx.author.voice.channel
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    await channel.connect(cls=NativeVoiceClient)



# Begins recording audio in voice channel.
@bot.command()
async def rec(ctx):
    # Start recording.
    ctx.voice_client.record(lambda e: print(f"Exception: {e}"))
    
    # Channel output message.
    embedVar = discord.Embed(title="Started the Recording!",
                             description="use >stop to stop!", 
                             color=0x546e7a)
    await ctx.send(embed=embedVar)



# Stops audio recording in voice channel. 
@bot.command()
async def stop(ctx: commands.Context):
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

    await process_prompt()
    await play(ctx)
    # await ctx.guild.voice_client.disconnect()



# Plays a specific audio file in VC.       
@bot.command() 
async def play(ctx):
    await ctx.guild.voice_client.disconnect()
    await asyncio.sleep(1)
    channel = ctx.author.voice.channel
    if channel is not None:
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio('response.wav'))
            while vc.is_playing():
                await asyncio.sleep(1)
            vc.stop()
            # await vc.disconnect()
    else:
        await ctx.channel.send("You are not in a voice channel.")
    
    # vc = ctx.guild.voice_client
    # await vc.disconnect()
    # await ctx.author.voice.channel.connect()
    # vc.play(discord.FFmpegPCMAudio('response.wav'))
    # while vc.is_playing():
    #     await asyncio.sleep(1)
    # vc.stop()



# Audio transcription.
async def transcribe_audio(audio_file):
    r = sr.Recognizer()

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    
    try:
        return r.recognize_google(audio, language='en-US')
    except sr.UnknownValueError:
        return "Error: Speech recognition could not understand the audio"
    except sr.RequestError as e:
        return f"Error: Could not request results from speech recognition service: {e}"
    



# Sends prompt to openai for text response.
async def prompt_openai(prompt):
    completion = openai.Completion.create(engine=model_engine,
                                          prompt=prompt,    
                                          max_tokens=1024,    
                                          n=1,
                                          stop=None,
                                          temperature=0.5,)

    response = completion.choices[0].text
    return response


    
# Text to speech, saves to file.
async def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.wav")
        
        

# Transcribes to text, text to OpenAI, reponse to speech.
async def process_prompt():
    transcription = await transcribe_audio("prompt.wav")
    response = await prompt_openai(transcription)
    await text_to_speech(response)



# BEFORE INVOKE ---------------------------------------------------------------



# Ran first when rec command is called.
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

  
        
# START BOT -------------------------------------------------------------------    

bot.run("MTA3MDI3ODcyNzU4MzQxMjI0NA.G_ly7p.U04jtq-KNc6mCcF1A3jRvT6QPr6_PsYAASlkjU")
