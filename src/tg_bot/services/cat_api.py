import aiohttp

from tg_bot.core.constants import CAT_API_URL, TIMEOUT


async def get_random_cat(http_session: aiohttp.ClientSession) -> str | None:
    """Возвращает ссылку на случайную картинку кота или None."""
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    try:
        async with http_session.get(CAT_API_URL, timeout=timeout) as response:
            if not response.ok:
                return None
            data = await response.json()
            return data[0]['url']
    except (
        TimeoutError,
        aiohttp.ClientError,
        KeyError,
        IndexError,
        TypeError,
    ):
        # API может не ответить или прислать неожиданный JSON.
        return None
