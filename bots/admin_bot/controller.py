from common_tools.async_connection import url_is_active
from consts import MySeria, Zetflix
from database.models import Admin, SerialSite


class AdminController:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._admin = None
        self._access_denied_msg = "Отказано в доступе"

    async def get_admin(self) -> Admin:
        if self._admin is None:
            self._admin = await Admin.get_object(self.user_id)
        return self._admin

    async def create_admin(self, new_admin_id: int) -> str:
        admin = await self.get_admin()
        admin.is_admin = True
        await admin.save()
        return f"Юзер с id {new_admin_id} теперь является администратором"

    async def delete_admin(self, admin_id: int) -> str:
        admin = await self.get_admin()
        if admin_id == admin.user_id:
            return "Вы не можете убрать с себя роль администратора"
        await Admin(admin_id, is_admin=False).save()
        return f"Юзер с id {admin_id} больше не является администратором"

    async def get_all_admins(self) -> str:
        admins = await Admin.get_admins_id()
        return "\n".join(admins)

    async def force_update_my_seria_url(self, new_url: str) -> str:
        """Обновляем ссылку на сайт MySeria"""
        try:
            serial_site = SerialSite(MySeria.KEY, new_url)
        except ValueError as err:
            return str(err)

        if await url_is_active(serial_site.url):
            if await serial_site.save():
                return f'Адрес успешно обновлён на: {serial_site.url}'
        return 'Не удалось обновить адрес'

    async def force_update_zetflix_url(self, new_url: str) -> str:
        """Обновляем ссылку на сайт Zetflix"""
        try:
            serial_site = SerialSite(Zetflix.KEY, new_url)
        except ValueError as err:
            return str(err)

        if await url_is_active(serial_site.url):
            if await serial_site.save():
                return f'Адрес успешно обновлён на: {serial_site.url}'
        return 'Не удалось обновить адрес'
