# admin.py

from aiogram import Router, F
from aiogram.types import Message
from config import Config
from database import get_db_connection

router = Router()


@router.message(F.text == "/stats")
async def admin_stats(message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]

        c.execute('SELECT SUM(balance) FROM users')
        total_balance = c.fetchone()[0] or 0

        c.execute('SELECT COUNT(*), SUM(amount) FROM withdrawals WHERE status = "pending"')
        pending_count, pending_amount = c.fetchone()

    await message.answer(
        f"""
📊 Bot Stats:
👥 মোট ইউজার: {total_users}
💰 মোট ব্যালেন্স: {total_balance} টাকা
⏳ পেন্ডিং উত্তোলন: {pending_count} ({pending_amount or 0} টাকা)
        """
    )
