import discord

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')


client.run("MTA3MDI3ODcyNzU4MzQxMjI0NA.G_ly7p.U04jtq-KNc6mCcF1A3jRvT6QPr6_PsYAASlkjU")
