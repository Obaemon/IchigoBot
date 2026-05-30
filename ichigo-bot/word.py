import random
from datetime import datetime, timezone, timedelta

def filter(words):
    now = datetime.now(timezone(timedelta(hours=9)))
    season_words = [word for word in words if word["month"] == now.month]

    season = (1 if now.month in [3, 4, 5] else
              2 if now.month in [6, 7, 8] else
              3 if now.month in [9, 10, 11] else
              4)

    season_words += [word for word in words if word["season"] == season]
    filtered_words = [word for word in words if word["month"] is None and word["season"] is None]


    return random.choice(random.choice([season_words, filtered_words]))