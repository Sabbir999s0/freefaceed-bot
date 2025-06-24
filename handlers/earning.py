from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_db_connection
from config import Config
import random
import string

class EarningStates(StatesGroup):
    watching_ad = State()

async def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = c.fetchone()
        
        if not user:
            # Create new user with referral code
            referral_code = await generate_referral_code()
            c.execute('''
                INSERT INTO users (user_id, username, full_name, referral_code)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, full_name, referral_code))
            conn.commit()
            
            # Check if user came from referral
            if len(message.text.split()) > 1:
                referrer_code = message.text.split()[1]
                c.execute('''
                    UPDATE users SET referred_by = ?
                    WHERE user_id = ?
                ''', (referrer_code, user_id))
                
                # Add bonus to referrer
                c.execute('''
                    UPDATE users SET balance = balance + ?
                    WHERE referral_code = ?
                ''', (Config.REFERRAL_BONUS, referrer_code))
                
                # Record the earning
                c.execute('''
                    INSERT INTO earnings (user_id, earning_type, amount)
                    VALUES ((SELECT user_id FROM users WHERE referral_code = ?), 'referral', ?)
                ''', (referrer_code, Config.REFERRAL_BONUS))
                
                conn.commit()
    
    welcome_message = f"""
👋 হ্যালো {full_name}! 

🟢 FreeFaceEd বটে আপনাকে স্বাগতম!

💰 আয় করার উপায়:
- 📢 প্রতিটি রেফারেলে {Config.REFERRAL_BONUS} টাকা
- 📺 প্রতিটি অ্যাড দেখলে {Config.AD_REWARD} টাকা
- 🎮 গেম খেলে জিতুন টাকা

💼 ব্যালেন্স চেক করতে: /balance
👥 রেফারেল লিঙ্ক: https://t.me/freefaceed_bot?start={referral_code}
🎮 গেম খেলতে: /games
💰 টাকা উত্তোলন: /withdraw
"""
    await message.answer(welcome_message)

async def watch_ad_handler(message: types.Message, state: FSMContext):
    await message.answer("📺 একটি অ্যাড দেখুন (30 সেকেন্ড)...")
    # Here you would integrate with actual ad network
    # For now, we'll simulate it
    
    # After ad is watched
    user_id = message.from_user.id
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', 
                  (Config.AD_REWARD, user_id))
        c.execute('INSERT INTO earnings (user_id, earning_type, amount) VALUES (?, ?, ?)',
                  (user_id, 'ad', Config.AD_REWARD))
        conn.commit()
    
    await message.answer(f"✅ আপনি {Config.AD_REWARD} টাকা অর্জন করেছেন!")

def register_earning_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=['start'])
    dp.register_message_handler(watch_ad_handler, commands=['watchad'])