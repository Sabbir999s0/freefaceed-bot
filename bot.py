import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import register_handlers
from database import init_db

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    init_db()
    logger.info("🤖 Bot is starting...")

    # Register all handlers
    register_handlers(dp)

    # Notify admin
    await bot.send_message(Config.ADMIN_IDS[0], "🤖 Bot started successfully!")

    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("⚠️ Bot shutdown")
