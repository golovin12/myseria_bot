import aiohttp


async def url_is_active(url: str, headers: dict | None = None) -> bool:
    async with aiohttp.request("GET", url, headers=headers) as response:
        if response.status == 200:
            return True
    return False
