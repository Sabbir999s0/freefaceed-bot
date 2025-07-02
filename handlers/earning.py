from aiogram import types, Router
from aiogram.filters import Command
from database import get_db_connection
from config import Config

router = Router()

@router.message(Command("earn"))
async def show_earn_menu(message: types.Message):
    text = """
🎯 আয় করার পদ্ধতি:

➤ রেফার করে আয় করুন: /refer  
➤ এড দেখুন এবং আয় করুন: /watchad
"""
    await message.answer(text)

@router.message(Command("refer"))
async def referral_info(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user{user_id}"

    referral_link = f"https://t.me/{(await message.bot.get_me()).username}?start={user_id}"

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE referred_by = ?", (str(user_id),))
        total_refs = c.fetchone()[0]

    await message.answer(
        f"👥 আপনার রেফারেল লিংক:\n{referral_link}\n\n"
        f"✅ মোট রেফার: {total_refs}\n"
        f"💸 প্রতি রেফারে ইনকাম: {Config.REFERRAL_BONUS} টাকা"
    )

@router.message(Command("watchad"))
async def watch_ad(message: types.Message):
    user_id = message.from_user.id

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (Config.AD_REWARD, user_id))
        c.execute("INSERT INTO earnings (user_id, earning_type, amount) VALUES (?, ?, ?)", (user_id, "ad", Config.AD_REWARD))
        conn.commit()

    await message.answer(f"🎉 বিজ্ঞাপন দেখায় {Config.AD_REWARD} টাকা ইনকাম হয়েছে!")

# ✅ এটা দরকার register_all_handlers এর জন্য
def register_earning_handlers(dp):
    dp.include_router(router)