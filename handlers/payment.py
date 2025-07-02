from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_db_connection
from config import Config

router = Router()

class WithdrawState(StatesGroup):
    amount = State()
    method = State()
    account = State()

@router.message(Command("withdraw"))
async def withdraw_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        balance = c.fetchone()["balance"]

    if balance < Config.MIN_WITHDRAWAL:
        await message.answer(f" ন্যূনতম উত্তোলন {Config.MIN_WITHDRAWAL} টাকা। আপনার ব্যালেন্স: {balance}")
        return

    await message.answer(" কত টাকা উত্তোলন করতে চান?")
    await state.set_state(WithdrawState.amount)

@router.message(WithdrawState.amount)
async def choose_method(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        if amount < Config.MIN_WITHDRAWAL:
            await message.answer(" ন্যূনতম সীমা পূরণ হয়নি।")
            return
        await state.update_data(amount=amount)

        btns = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btns.add("বিকাশ", "নগদ", "রকেট")
        await message.answer(" পেমেন্ট মেথড নির্বাচন করুন:", reply_markup=btns)
        await state.set_state(WithdrawState.method)
    except:
        await message.answer(" দয়া করে একটি সংখ্যা দিন।")

@router.message(WithdrawState.method)
async def ask_account(message: types.Message, state: FSMContext):
    if message.text not in ["বিকাশ", "নগদ", "রকেট"]:
        await message.answer(" সঠিক মেথড দিন।")
        return
    await state.update_data(method=message.text)
    await message.answer(" একাউন্ট নম্বর দিন:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(WithdrawState.account)

@router.message(WithdrawState.account)
async def confirm_withdraw(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (data["amount"], user_id))
        c.execute("INSERT INTO withdrawals (user_id, amount, method, account_info) VALUES (?, ?, ?, ?)",
                  (user_id, data["amount"], data["method"], message.text))
        conn.commit()

    await message.answer(" উত্তোলনের অনুরোধ পাঠানো হয়েছে, অ্যাডমিন চেক করবে।")
    await state.clear()

#  এইটা না থাকলে import error আসবে
def register_payment_handlers(dp):
    dp.include_router(router)