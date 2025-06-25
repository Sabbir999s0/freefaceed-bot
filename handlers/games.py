# games.py

from aiogram import Router, F
from aiogram.types import Message
from config import Config
from database import get_db_connection
import random

router = Router()


@router.message(F.text.in_({"/games", "/game"}))
async def games_menu(message: Message):
    await message.answer(
        f"""
🎮 গেম মেনু:

1. 🎲 ডাইস গেম - /dice

💰 বাজি সীমা: {Config.MIN_BET} থেকে {Config.MAX_BET} টাকা
        """
    )


@router.message(F.text == "/dice")
async def start_dice_game(message: Message):
    await message.answer("🎲 ডাইস গেম শুরু!\nআপনার বাজির পরিমাণ দিন (সংখ্যা):")


@router.message(lambda msg: msg.text.isdigit())
async def process_dice_bet(message: Message):
    user_id = message.from_user.id
    bet_amount = int(message.text)

    if not (Config.MIN_BET <= bet_amount <= Config.MAX_BET):
        await message.answer(f"বাজি {Config.MIN_BET}-{Config.MAX_BET} টাকার মধ্যে হতে হবে।")
        return

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()

        if not row or row["balance"] < bet_amount:
            await message.answer("❌ পর্যাপ্ত ব্যালেন্স নেই।")
            return

        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bet_amount, user_id))

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            win_amount = bet_amount * 2
            result = "win"
            msg = f"✅ আপনি জিতেছেন {win_amount} টাকা! 🎉"
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win_amount, user_id))
        elif user_roll == bot_roll:
            win_amount = bet_amount
            result = "draw"
            msg = f"🤝 ড্র হয়েছে, আপনি ফেরত পেয়েছেন {win_amount} টাকা।"
            c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (win_amount, user_id))
        else:
            win_amount = 0
            result = "lose"
            msg = f"😢 আপনি হারিয়েছেন {bet_amount} টাকা।"

        c.execute('''
            INSERT INTO games (user_id, game_type, bet_amount, win_amount, result)
            VALUES (?, "dice", ?, ?, ?)
        ''', (user_id, bet_amount, win_amount, result))

        conn.commit()

    await message.answer(
        f"🎲 আপনি: {user_roll} | 🤖 বট: {bot_roll}\n\n{msg}"
    )
