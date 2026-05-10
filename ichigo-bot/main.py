import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

import database
import date_string

database.init_db()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not found.")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(
    command_prefix="!",
    intents=intents,
)
tree = client.tree

@client.event
async def on_ready():
    await tree.sync()
    print(f"ログイン成功: {client.user.display_name}")
    print(f"次回のいちごつみ歌会開始日時: {date_string.next_sunday_8am_jst()}")

@client.event
async def on_message(message):
    print(f"from {message.author.display_name}: {message.content}")

    # チャンネルIDが事前に指定したいちごつみスレッド以外の場合は何もしない
    if message.channel.id != int(os.getenv("CHANNEL_ID") or 0):
        return

    # このbotが送信したメッセージの場合は何もしない
    if message.author == client.user:
        return
    
    ichigotsumi_id = None
    previous_message_id = None
    # メッセージが返信の場合、返信元がどの歌会のものかを特定する
    if message.reference is not None:
        reference_message = database.get_post_from_message_id(message.reference.message_id)
        if reference_message:
            ichigotsumi_id = reference_message["ichigotsumi_id"]
            previous_message_id = reference_message["message_id"]

    # 歌会が特定できない場合は、新規企画歌会を作成する
    if ichigotsumi_id is None:
        print("新規歌会を作成します。")
        ichigotsumi_id = database.create_ichigotsumi(message.author.id, date_string.iso_from_discord(message.created_at), None)

    database.create_post(
        message.author.id,
        message.author.display_name,
        message.content,
        date_string.iso_from_discord(message.created_at),
        ichigotsumi_id,
        message.id,
        previous_message_id
    )

@tree.command(name="ichigo_join", description="いちごつみ当番に参加")
async def ichigo_join(interaction: discord.Interaction):
    print(f"参加コマンドが呼び出されました: {interaction.user.id}")
    leaders = database.get_leaders()
    print(leaders)
    leader = next((leader for leader in leaders if leader["user_id"] == str(interaction.user.id)), None)
    print(leader)

    if not leader:
        database.set_leader(interaction.user.id, interaction.user.name)
        await interaction.response.send_message(f"いちごつみ当番に参加しました。", ephemeral=True)
        return

    else:
        if leader["user_name"] != interaction.user.name:
            database.set_leader(interaction.user.id, interaction.user.name)
            await interaction.response.send_message(f"当番のユーザー名を更新しました。", ephemeral=True)
            return

        await interaction.response.send_message(f"すでにいちごつみ当番に参加しています。", ephemeral=True)

@tree.command(name="ichigo_unjoin", description="いちごつみ当番から離脱")
async def ichigo_unjoin(interaction: discord.Interaction):
    print(f"離脱コマンドが呼び出されました: {interaction.user.id}")
    is_deleted = database.delete_leader(interaction.user.id)

    if is_deleted:
        await interaction.response.send_message(f"いちごつみ当番から離脱しました。", ephemeral=True)
    else:
        await interaction.response.send_message(f"いちごつみ当番に参加していません。", ephemeral=True)

client.run(TOKEN)