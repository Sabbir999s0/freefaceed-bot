import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

    REFERRAL_BONUS = 5
    AD_REWARD = 1
    MIN_WITHDRAWAL = 50
    MIN_BET = 5
    MAX_BET = 1000