import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import random
from discord.ext import tasks
from datetime import time, datetime, timezone, timedelta

import database
import date_string
import word

database.init_db()
database.reload_words()

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not found.")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(
    command_prefix="/",
    intents=intents,
)
tree = client.tree

# 日本時間土曜日10時に常設歌会の当番を選出し、常設歌会を設定する
@tasks.loop(time=time(hour=20, minute=59, tzinfo=timezone(timedelta(hours=9))))
async def request_weekly_topic():
    # if datetime.now().weekday() != 5:
    #     print("曜日判定: False")
    #     return
    
    next_leader = None
    leaders = database.get_leaders()
    if len(leaders) == 1:
        next_leader = leaders[0]
    elif len(leaders) != 0:
        filtered_leaders = leaders
        topics = database.get_recent_topics(len(leaders) - 1)
        for topic in topics:
            filtered_leaders = [leader for leader in filtered_leaders if leader["user_id"] != topic["leader_user_id"]]
        if len(filtered_leaders) == 0:
            filtered_leaders = leaders
        next_leader = random.choice(filtered_leaders)
    print("当番選出処理: ", next_leader["user_name"] if next_leader else "当番なし")

    if next_leader:
        user = await client.fetch_user(int(next_leader["user_id"]))
        try:
            await user.send("次回歌会の当番に選ばれました。お題の短歌か言葉を送信してください！\nお題を取り消したい場合は「!」を送信してください。")
        except discord.Forbidden:
            print(f" {next_leader['user_name']} にDMを送信できませんでした。")



    ichigotsumi_id = database.create_ichigotsumi(
        next_leader["user_id"] if next_leader else None,
        date_string.utc_iso_from_jst(days_ahead=1, hour=8, minute=0, second=0),
        date_string.utc_iso_from_jst(days_ahead=8, hour=7, minute=59, second=59)
    )
    database.create_topic(
        ichigotsumi_id,
        date_string.utc_iso_from_jst(days_ahead=0, hour=10, minute=0, second=0),
        date_string.utc_iso_from_jst(days_ahead=1, hour=7, minute=55, second=59),
        next_leader["user_id"] if next_leader else None
    )

# 日本時間日曜日8時に常設歌会を開始する
@tasks.loop(time=time(hour=20, minute=25, tzinfo=timezone(timedelta(hours=9))))
async def start_weekly_ichigotsumi():
    # if datetime.now().weekday() != 6:
    #     print("曜日判定: False")
    #     return
    
    print("常設歌会を開始します。")
    ichigotsumi = database.get_ichigotsumi_from_start_date(date_string.utc_iso_from_jst(days_ahead=0, hour=8, minute=0, second=0))
    # if ichigotsumi is None:
    #     print("常設歌会が見つかりませんでした。")
    #     return
    
    # contents = database.get_topic_from_ichigotsumi_id(ichigotsumi["id"])["contents"]
    contents = None
    if contents is None:
        words = database.get_word_list()
        contents = word.filter(words)["word"]

    channel = await client.fetch_channel(int(os.getenv("CHANNEL_ID") or 0))
    await channel.send("今週のお題\n\n" + contents)




@client.event
async def on_ready():
    await tree.sync()

    if not start_weekly_ichigotsumi.is_running():
        start_weekly_ichigotsumi.start()
    
    if not request_weekly_topic.is_running():
        request_weekly_topic.start()

    print(f"ログイン成功: {client.user.display_name}")

@client.event
async def on_message(message):
    print(f"from {message.author.display_name}: {message.content}")

    # このbotが送信したメッセージの場合は何もしない
    if message.author == client.user:
        return

    # DMの場合は当番のお題設定処理を行う
    if message.guild is None:
        topic = database.get_topic_opening_now()
        print(dict(topic))
        if topic and topic["leader_user_id"] == str(message.author.id):
            print("お題：", message.content.strip())
            if message.content.strip() == "!" or message.content.strip() == "！":
                database.update_topic(message.author.id, None)
                await message.channel.send("お題を取り消しました。")
            else:
                database.update_topic(message.author.id, message.content.strip())
                await message.channel.send("お題を設定しました。")
        else:
            await message.channel.send("現在お題を受付しておりません。")

    # チャンネルIDが事前に指定したいちごつみスレッド以外の場合は何もしない
    if message.channel.id != int(os.getenv("CHANNEL_ID") or 0):
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