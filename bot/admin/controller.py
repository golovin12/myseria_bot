import aiohttp

from bot.consts import MY_SERIA_KEY
from bot.database.models import User, SerialSite


class AdminController:
    def __init__(self, user_id: int):
        self.user = User(user_id)
        self._access_denied_msg = "Отказано в доступе"

    async def create_admin(self, new_admin_id: int) -> str:
        if not await self.user.is_admin():
            return self._access_denied_msg
        await User(new_admin_id).set_is_admin()
        return f"Юзер с id {new_admin_id} теперь является администратором"

    async def delete_admin(self, admin_id: int) -> str:
        if admin_id == self.user.user_id or not await self.user.is_admin():
            return self._access_denied_msg
        await User(admin_id).del_is_admin()
        return f"Юзер с id {admin_id} больше не является администратором"

    async def get_all_admins(self) -> str:
        if not await self.user.is_admin():
            return self._access_denied_msg
        admins = await self.user.get_all_admins()
        return "\n".join(admins)

    async def force_update_my_seria_url(self, new_url: str) -> str:
        """Обновляем ссылку на сайт MySeria"""
        if not await self.user.is_admin():
            return self._access_denied_msg
        async with aiohttp.request("GET", new_url) as response:
            if response.status == 200:
                await SerialSite(MY_SERIA_KEY).set_url(new_url)
                return f'Адрес успешно обновлён на: {new_url}'
        return 'Не удалось обновить адрес'
