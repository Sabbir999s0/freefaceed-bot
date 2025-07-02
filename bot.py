from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging

from config import Config
from database import init_db
from handlers import register_all_handlers
from aiogram.client.default import DefaultBotProperties  #  নতুন লাইন

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  #  fix করা লাইন
    )
    dp = Dispatcher(storage=MemoryStorage())

    init_db()
    register_all_handlers(dp)

    await bot.send_message(Config.ADMIN_IDS[0], " Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())