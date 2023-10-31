import aiohttp


async def url_is_active(url: str) -> bool:
    async with aiohttp.request("GET", url) as response:
        if response.status == 200:
            return True
    return False
