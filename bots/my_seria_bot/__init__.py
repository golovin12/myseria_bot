from aiogram import Router

from .handler_errors import router as errors_router
from .handler_paginator import router as paginate_router
from .handlers import router as user_router
from .keyboards import get_menu_commands

router = Router()
router.include_router(errors_router)
router.include_router(paginate_router)
router.include_router(user_router)
menu_commands = get_menu_commands()

__all__ = ('router', 'menu_commands')
