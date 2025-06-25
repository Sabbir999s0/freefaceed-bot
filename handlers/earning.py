# earning.py

from aiogram import Router, F
from aiogram.types import Message
from config import Config
from database import get_db_connection
import random, string

router = Router()


def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


@router.message(F.text.startswith("/start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    with get_db_connection() as conn:
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()

        if not user:
            referral_code = generate_referral_code()
            c.execute(
                'INSERT INTO users (user_id, username, full_name, referral_code) VALUES (?, ?, ?, ?)',
                (user_id, username, full_name, referral_code)
            )

            if len(message.text.split()) > 1:
                ref_code = message.text.split()[1]
                c.execute('UPDATE users SET referred_by = ? WHERE user_id = ?', (ref_code, user_id))
                c.execute('UPDATE users SET balance = balance + ? WHERE referral_code = ?', (Config.REFERRAL_BONUS, ref_code))
                c.execute('INSERT INTO earnings (user_id, earning_type, amount) VALUES ((SELECT user_id FROM users WHERE referral_code = ?), "referral", ?)',
                          (ref_code, Config.REFERRAL_BONUS))
            conn.commit()

    await message.answer(
        f"""
👋 হ্যালো {full_name}!

🟢 FreeFaceEd বটে স্বাগতম!

💰 আয় করার উপায়:
- 📢 প্রতি রেফারেলে {Config.REFERRAL_BONUS} টাকা
- 📺 অ্যাড দেখলে {Config.AD_REWARD} টাকা

রেফারেল লিংক: https://t.me/freefaceed_bot?start={referral_code}
        """
    )


@router.message(F.text == "/watchad")
async def watch_ad_handler(message: Message):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (Config.AD_REWARD, user_id))
        c.execute('INSERT INTO earnings (user_id, earning_type, amount) VALUES (?, "ad", ?)', (user_id, Config.AD_REWARD))
        conn.commit()

    await message.answer(f"✅ আপনি {Config.AD_REWARD} টাকা অর্জন করেছেন!")
