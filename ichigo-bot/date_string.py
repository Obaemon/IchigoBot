from datetime import datetime, timedelta, timezone

# Discord APIの日時のテキストをISO形式に変換する
def iso_from_discord(date_string):
    return date_string.replace(microsecond=0).isoformat()

# 次の日曜8時（JST）をUTCのISO形式で返す
def next_sunday_8am_jst():
    now = datetime.now(timezone.utc)

    # JSTに変換（基準を日本時間にする）
    jst = timezone(timedelta(hours=9))
    now_jst = now.astimezone(jst)

    # 今日から次の日曜までの日数
    days_ahead = (6 - now_jst.weekday()) % 7

    # もし「今日が日曜で8時過ぎ」なら次週にする
    target = now_jst.replace(hour=8, minute=0, second=0, microsecond=0)
    if days_ahead == 0 and now_jst >= target:
        days_ahead = 7

    # 次の日曜8時（JST）
    next_sunday_jst = target + timedelta(days=days_ahead)

    # UTCに戻す
    next_sunday_utc = next_sunday_jst.astimezone(timezone.utc)

    return next_sunday_utc.isoformat()