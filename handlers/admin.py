from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_db_connection
from config import Config

async def admin_stats(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Total users
        c.execute('SELECT COUNT(*) FROM users')
        total_users = c.fetchone()[0]
        
        # New users today
        c.execute('SELECT COUNT(*) FROM users WHERE date(join_date) = date("now")')
        new_users_today = c.fetchone()[0]
        
        # Total balance
        c.execute('SELECT SUM(balance) FROM users')
        total_balance = c.fetchone()[0] or 0
        
        # Pending withdrawals
        c.execute('SELECT COUNT(*), SUM(amount) FROM withdrawals WHERE status = "pending"')
        pending_withdrawals = c.fetchone()
        
        # Earnings stats
        c.execute('SELECT earning_type, SUM(amount) FROM earnings GROUP BY earning_type')
        earnings = c.fetchall()
    
    stats_text = f"""
📊 বট পরিসংখ্যান:

👥 ব্যবহারকারী:
- মোট: {total_users}
- আজ নতুন: {new_users_today}

💰 ব্যালেন্স:
- মোট ব্যালেন্স: {total_balance} টাকা

💸 উত্তোলন:
- পেন্ডিং: {pending_withdrawals[0]} (মোট {pending_withdrawals[1] or 0} টাকা)

📈 আয়:
"""
    for earning in earnings:
        stats_text += f"- {earning[0]}: {earning[1]} টাকা\n"
    
    await message.answer(stats_text)

async def process_withdrawal(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return
    
    if not message.reply_to_message or not message.reply_to_message.text.startswith("Withdrawal ID:"):
        await message.answer("দয়া করে উত্তোলন রিকোয়েস্টে রিপ্লাই করুন")
        return
    
    try:
        command, withdrawal_id = message.text.split()
        withdrawal_id = int(withdrawal_id)
    except:
        await message.answer("ব্যবহার: /approve <id> অথবা /reject <id>")
        return
    
    valid_status = "approved" if command == "/approve" else "rejected"
    
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Get withdrawal info
        c.execute('SELECT user_id, amount FROM withdrawals WHERE id = ?', (withdrawal_id,))
        withdrawal = c.fetchone()
        
        if not withdrawal:
            await message.answer("উত্তোলন রিকোয়েস্ট খুঁজে পাওয়া যায়নি")
            return
            
        if valid_status == "approved":
            # Mark as approved
            c.execute('UPDATE withdrawals SET status = ? WHERE id = ?', 
                     ("approved", withdrawal_id))
        else:
            # Reject and return balance
            c.execute('UPDATE withdrawals SET status = ? WHERE id = ?', 
                     ("rejected", withdrawal_id))
            c.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?',
                     (withdrawal['amount'], withdrawal['user_id']))
        
        conn.commit()
    
    # Notify user
    try:
        if valid_status == "approved":
            await message.bot.send_message(
                withdrawal['user_id'],
                f"✅ আপনার {withdrawal['amount']} টাকার উত্তোলন অনুমোদিত হয়েছে!"
            )
        else:
            await message.bot.send_message(
                withdrawal['user_id'],
                f"❌ আপনার {withdrawal['amount']} টাকার উত্তোলন প্রত্যাখ্যান হয়েছে। টাকা আপনার ব্যালেন্সে ফেরত দেওয়া হয়েছে।"
            )
    except:
        pass
    
    await message.answer(f"উত্তোলন রিকোয়েস্ট #{withdrawal_id} {valid_status} করা হয়েছে")

def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_stats, commands=['stats'])
    dp.register_message_handler(process_withdrawal, commands=['approve', 'reject'])