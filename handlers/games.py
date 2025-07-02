from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db_connection
from config import Config
import random

router = Router()

class BetState(StatesGroup):
    waiting_for_bet = State()

@router.message(Command("bet"))
async def start_bet(message: types.Message, state: FSMContext):
    await message.answer(f" কত টাকা বেট করতে চান? (মিনিমাম {Config.MIN_BET})")
    await state.set_state(BetState.waiting_for_bet)

@router.message(BetState.waiting_for_bet)
async def process_bet(message: types.Message, state: FSMContext):
    try:
        bet = int(message.text)
        if bet < Config.MIN_BET or bet > Config.MAX_BET:
            await message.answer(f" বেট সীমা: {Config.MIN_BET} - {Config.MAX_BET}")
            return

        user_id = message.from_user.id
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            row = c.fetchone()
            if not row or row["balance"] < bet:
                await message.answer(" পর্যাপ্ত ব্যালেন্স নেই।")
                await state.clear()
                return

            win = random.choice([True, False])
            win_amount = bet * 2 if win else 0
            result = "win" if win else "lose"

            new_balance = row["balance"] - bet + win_amount

            c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            c.execute("INSERT INTO games (user_id, game_type, bet_amount, win_amount, result) VALUES (?, ?, ?, ?, ?)",
                      (user_id, "coin", bet, win_amount, result))
            conn.commit()

        await message.answer(f" রেজাল্ট: {' জিতেছেন!' if win else ' হেরে গেছেন!'}\n নতুন ব্যালেন্স: {new_balance}")
        await state.clear()

    except ValueError:
        await message.answer(" দয়া করে একটি সংখ্যা লিখুন।")

#  এইটা অবশ্যই লাগবে যাতে init.py থেকে call করতে পারো
def register_games_handlers(dp):
    dp.include_router(router)