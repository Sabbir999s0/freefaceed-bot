from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_db_connection
from config import Config

class WithdrawalStates(StatesGroup):
    choosing_amount = State()
    choosing_method = State()
    providing_details = State()

async def withdraw_menu(message: types.Message):
    user_id = message.from_user.id
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = c.fetchone()['balance']
    
    menu_text = f"""
💰 উত্তোলন মেনু:

বর্তমান ব্যালেন্স: {balance} টাকা
ন্যূনতম উত্তোলন: {Config.MIN_WITHDRAWAL} টাকা

উত্তোলন করতে: /withdraw
"""
    await message.answer(menu_text)

async def start_withdrawal(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
        balance = c.fetchone()['balance']
    
    if balance < Config.MIN_WITHDRAWAL:
        await message.answer(f"ন্যূনতম উত্তোলনযোগ্য পরিমাণ {Config.MIN_WITHDRAWAL} টাকা। আপনার ব্যালেন্স {balance} টাকা।")
        return
    
    await message.answer(f"আপনার উত্তোলনযোগ্য ব্যালেন্স: {balance} টাকা\n\nকত টাকা উত্তোলন করতে চান?")
    await WithdrawalStates.choosing_amount.set()

async def process_withdrawal_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text)
        user_id = message.from_user.id
        
        if amount < Config.MIN_WITHDRAWAL:
            await message.answer(f"ন্যূনতম উত্তোলন {Config.MIN_WITHDRAWAL} টাকা")
            return
            
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            balance = c.fetchone()['balance']
            
            if amount > balance:
                await message.answer("আপনার ব্যালেন্স পর্যাপ্ত নয়")
                await state.finish()
                return
                
            await state.update_data(amount=amount)
            
            # Show payment methods
            methods_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            methods_keyboard.add("বিকাশ", "নগদ", "রকেট")
            methods_keyboard.add("❌ বাতিল")
            
            await message.answer("পেমেন্ট মেথড নির্বাচন করুন:", reply_markup=methods_keyboard)
            await WithdrawalStates.next()
            
    except ValueError:
        await message.answer("দয়া করে একটি সঠিক সংখ্যা লিখুন")

async def process_withdrawal_method(message: types.Message, state: FSMContext):
    if message.text == "❌ বাতিল":
        await message.answer("উত্তোলন বাতিল করা হয়েছে", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        return
        
    valid_methods = ["বিকাশ", "নগদ", "রকেট"]
    if message.text not in valid_methods:
        await message.answer("অনুগ্রহ করে একটি বৈধ পদ্ধতি নির্বাচন করুন")
        return
        
    await state.update_data(method=message.text)
    await message.answer("আপনার একাউন্ট নম্বর লিখুন (যেমন: 01XXXXXXXXX):", reply_markup=types.ReplyKeyboardRemove())
    await WithdrawalStates.next()

async def process_withdrawal_details(message: types.Message, state: FSMContext):
    account_info = message.text
    user_id = message.from_user.id
    user_data = await state.get_data()
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Deduct balance
        c.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?',
                 (user_data['amount'], user_id))
        
        # Create withdrawal request
        c.execute('''
            INSERT INTO withdrawals (user_id, amount, method, account_info)
            VALUES (?, ?, ?, ?)
        ''', (user_id, user_data['amount'], user_data['method'], account_info))
        
        conn.commit()
    
    await message.answer(f"""
✅ আপনার উত্তোলন রিকোয়েস্ট জমা হয়েছে!

পরিমাণ: {user_data['amount']} টাকা
পদ্ধতি: {user_data['method']}
একাউন্ট: {account_info}

অ্যাডমিন অনুমোদনের পর টাকা পাঠানো হবে।
""")
    await state.finish()

def register_payment_handlers(dp: Dispatcher):
    dp.register_message_handler(withdraw_menu, commands=['withdraw', 'payment'])
    dp.register_message_handler(start_withdrawal, commands=['withdraw'])
    dp.register_message_handler(process_withdrawal_amount, state=WithdrawalStates.choosing_amount)
    dp.register_message_handler(process_withdrawal_method, state=WithdrawalStates.choosing_method)
    dp.register_message_handler(process_withdrawal_details, state=WithdrawalStates.providing_details)