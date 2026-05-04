# IchigoBot
Discordいちごつみ短歌集計botです。

## 環境構築

クローンしたら ./ichigo-bot/sql にそれぞれの環境用のSQLiteを配置する。

.env を作成して DISCORD_TOKEN と CHANNEL_ID を追加する。

./ichigo-bot に移動して uv run python main.py で起動  

開発環境でのDBリセットは ./ichigo-bot/tanka.db を削除  
