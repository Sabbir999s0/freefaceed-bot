# payment.py

from aiogram import Router, F
from aiogram.types import Message
from config import Config
from database import get_db_connection

router = Router()


@router.message(F.text == "/withdraw")
async def withdraw_info(message: Message):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        balance = c.fetchone()["balance"]

    if balance < Config.MIN_WITHDRAWAL:
        await message.answer(f"❌ আপনার ব্যালেন্স {balance} টাকা। উত্তোলনের জন্য অন্তত {Config.MIN_WITHDRAWAL} টাকা লাগবে।")
    else:
        await message.answer(
            f"""
✅ আপনার ব্যালেন্স: {balance} টাকা

উত্তোলনের জন্য অ্যাডমিনের সাথে যোগাযোগ করুন।
        """
        )
