from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import Config
import logging

# Initialize bot and dispatcher
bot = Bot(token=Config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def on_startup(dp):
    from database import init_db
    init_db()
    logger.info("Bot started")
    await bot.send_message(Config.ADMIN_IDS[0], "🤖 Bot started successfully!")

async def on_shutdown(dp):
    logger.info("Bot shutting down...")
    await bot.send_message(Config.ADMIN_IDS[0], "⚠️ Bot shutting down...")
    await dp.storage.close()
    await dp.storage.wait_closed()

# Import handlers
from handlers import register_handlers
register_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(
        dp,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True
    )