from typing import Type

from .user_base_handler import UserHandler
from .command_add_serial import CommandAddSerial
from .command_cancel import CommandCancel
from .command_delete_serial import CommandDeleteSerial
from .command_help import CommandHelp
from .command_new_series import CommandNewSeries
from .command_reboot import CommandReboot
from .command_serial_info import CommandSerialInfo
from .command_start import CommandStart
from .command_actual_url import CommandActualUrl
from .paginator import Paginator

handler_classes: tuple[Type[UserHandler], ...] = (
    CommandAddSerial, CommandCancel, CommandDeleteSerial, CommandHelp, CommandNewSeries, CommandReboot,
    CommandSerialInfo, CommandStart, CommandActualUrl, Paginator
)

__all__ = ('handler_classes', 'UserHandler')
