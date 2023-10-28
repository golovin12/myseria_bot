from aiogram import Router

from .handler_errors import router as errors_router
from .handlers import router as admin_router

router = Router()
router.include_router(errors_router)
router.include_router(admin_router)

__all__ = ('router',)
