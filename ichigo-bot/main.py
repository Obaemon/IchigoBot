import discord
import os
from dotenv import load_dotenv

import database

database.init_db()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"ログイン成功: {client.user}")

@client.event
async def on_message(message):
    print(f"from {message.author}: {message.content}")

    if message.channel.id != int(os.getenv("CHANNEL_ID") or 0):
        return

    if message.author == client.user:
        return
    
    event_id = None
    previous_message_id = None
    if message.reference is not None:
        referenced_tanka = database.get_tanka_from_message_id(message.reference.message_id)
        if referenced_tanka:
            event_id = referenced_tanka["event_id"]
            previous_message_id = referenced_tanka["previous_message_id"]
    else:
        event_id = database.create_event(None, message.created_at, None)

    database.create_tanka(message.content, message.author.id, message.author.name, message.created_at, event_id, message.id, previous_message_id)

client.run(TOKEN)

database.create_event("テスト大会", "2026-05-03", "2026-05-10")