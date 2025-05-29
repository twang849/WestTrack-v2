import discord
from agentic.common import Agent
from academic_advisor import academic_advisor  # Import your agent

TOKEN = "MTM3NDU0NTY3MzkxNDk0MTUyMg.GTkLOf.02hin6V2onJ_5Rc1QnGfp1-UD96hd5dsK6Ynuo"  # Replace with your bot token

intents = discord.Intents.default()
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    # Prevent the bot from replying to itself
    if message.author == client.user:
        return

    # You can add more sophisticated command parsing here
    user_input = message.content
    # Run the agent synchronously (adjust if your agent is async)
    response = academic_advisor.run(user_input)
    await message.channel.send(response)

client.run(TOKEN)