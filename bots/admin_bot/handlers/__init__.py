from typing import Type

from .admin_base_handler import AdminHandler
from .command_create_admin import CommandCreateAdmin
from .command_delete_admin import CommandDeleteAdmin
from .command_help import CommandHelp
from .command_new_my_seria_addr import CommandNewMySeriaAddr
from .command_new_zetflix_addr import CommandNewZetflixAddr
from .command_show_admins import CommandShowAdmins

handler_classes: tuple[Type[AdminHandler], ...] = (
    CommandCreateAdmin, CommandDeleteAdmin, CommandHelp, CommandNewMySeriaAddr, CommandNewZetflixAddr,
    CommandShowAdmins
)

__all__ = ('handler_classes', 'AdminHandler')
