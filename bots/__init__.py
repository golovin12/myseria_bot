from .admin_bot import router as admin_router
from .my_seria_bot import router as my_seria_router
from .my_seria_bot import menu_commands as my_seria_menu_commands
from .my_seria_bot.my_seria.parser import update_my_seria_url_by_vk

__all__ = ('admin_router', 'my_seria_router', 'my_seria_menu_commands', 'update_my_seria_url_by_vk')
