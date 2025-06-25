# handlers/__init__.py
from aiogram import Dispatcher
from .earning import register_earning_handlers
from .games import register_games_handlers
from .admin import register_admin_handlers
from .payment import register_payment_handlers

def register_handlers(dp: Dispatcher):
    register_earning_handlers(dp)
    register_games_handlers(dp)
    register_admin_handlers(dp)
    register_payment_handlers(dp)
