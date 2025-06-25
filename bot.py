# bot.py
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
import asyncio
import logging

from config import Config
from database import init_db
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

register_handlers(dp)

async def on_startup():
    init_db()
    logger.info("Bot started")
    await bot.send_message(Config.ADMIN_IDS[0], "🤖 Bot started successfully!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
