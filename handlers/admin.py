from aiogram import types, Router
from aiogram.filters import Command
from config import Config

router = Router()

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        await message.answer(" আপনি অ্যাডমিন নন।")
        return

    await message.answer(" অ্যাডমিন কমান্ড:\n/stats\n/broadcast")
    
# ভবিষ্যতে এখানে stats বা broadcast কমান্ড যুক্ত করতে পারো

def register_admin_handlers(dp):
    dp.include_router(router)