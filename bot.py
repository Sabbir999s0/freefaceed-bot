# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from database import init_db
from handlers import register_handlers

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot init
bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

async def on_startup():
    init_db()
    logger.info("Bot started")
    if Config.ADMIN_IDS:
        await bot.send_message(Config.ADMIN_IDS[0], "🤖 Bot started successfully!")

async def on_shutdown():
    logger.info("Bot shutting down...")
    if Config.ADMIN_IDS:
        await bot.send_message(Config.ADMIN_IDS[0], "⚠️ Bot shutting down...")

async def main():
    await on_startup()
    register_handlers(dp)
    await dp.start_polling(bot)
    await on_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
