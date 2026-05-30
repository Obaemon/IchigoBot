from datetime import time, datetime, timedelta, timezone

# Discord APIの日時のテキストをISO形式に変換する
def iso_from_discord(date_string):
    return date_string.replace(microsecond=0).isoformat()

def utc_iso_from_jst(days_ahead, hour=0, minute=0, second=0):
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    target = now.replace(hour=hour, minute=minute, second=second, microsecond=0)
    target = target + timedelta(days=days_ahead)
    target = target.astimezone(timezone.utc)
    return target.isoformat()
