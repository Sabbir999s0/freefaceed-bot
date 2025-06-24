from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_db_connection
from config import Config
import random

class GameStates(StatesGroup):
    choosing_bet = State()
    playing_game = State()

async def games_menu(message: types.Message):
    menu_text = """
🎮 গেম মেনু:

1. 🎲 ডাইস গেম - /dice
2. 🏀 বাস্কেটবল - /basketball
3. ⚽ ফুটবল - /football

💰 বর্তমান বাজি: {min_bet} থেকে {max_bet} টাকা
""".format(min_bet=Config.MIN_BET, max_bet=Config.MAX_BET)
    
    await message.answer(menu_text)

async def start_dice_game(message: types.Message, state: FSMContext):
    await message.answer("🎲 ডাইস গেম\n\nআপনার বাজির পরিমাণ লিখুন:")
    await GameStates.choosing_bet.set()

async def process_bet(message: types.Message, state: FSMContext):
    try:
        bet_amount = int(message.text)
        user_id = message.from_user.id
        
        if bet_amount < Config.MIN_BET:
            await message.answer(f"ন্যূনতম বাজি {Config.MIN_BET} টাকা")
            return
        if bet_amount > Config.MAX_BET:
            await message.answer(f"সর্বোচ্চ বাজি {Config.MAX_BET} টাকা")
            return
            
        # Check balance
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            balance = c.fetchone()['balance']
            
            if balance < bet_amount:
                await message.answer("আপনার ব্যালেন্স পর্যাপ্ত নয়")
                await state.finish()
                return
                
            # Deduct bet amount
            c.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?',
                     (bet_amount, user_id))
            
            # Play game
            bot_roll = random.randint(1, 6)
            user_roll = random.randint(1, 6)
            
            if user_roll > bot_roll:
                win_amount = bet_amount * 2
                result = "win"
                message_text = f"🎲 আপনি রোল করেছেন: {user_roll}\n🤖 বট রোল করেছে: {bot_roll}\n\n🎉 আপনি জিতেছেন {win_amount} টাকা!"
            elif user_roll == bot_roll:
                win_amount = bet_amount
                result = "draw"
                message_text = f"🎲 আপনি রোল করেছেন: {user_roll}\n🤖 বট রোল করেছে: {bot_roll}\n\n🤝 ড্র! আপনি ফেরত পেয়েছেন {win_amount} টাকা"
            else:
                win_amount = 0
                result = "lose"
                message_text = f"🎲 আপনি রোল করেছেন: {user_roll}\n🤖 বট রোল করেছে: {bot_roll}\n\n😢 আপনি হারেছেন {bet_amount} টাকা"
            
            if win_amount > 0:
                c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?',
                         (win_amount, user_id))
            
            # Record game
            c.execute('''
                INSERT INTO games (user_id, game_type, bet_amount, win_amount, result)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, 'dice', bet_amount, win_amount, result))
            
            conn.commit()
            
        await message.answer(message_text)
        await state.finish()
        
    except ValueError:
        await message.answer("দয়া করে একটি সঠিক সংখ্যা লিখুন")

def register_games_handlers(dp: Dispatcher):
    dp.register_message_handler(games_menu, commands=['games', 'game'])
    dp.register_message_handler(start_dice_game, commands=['dice'])
    dp.register_message_handler(process_bet, state=GameStates.choosing_bet)