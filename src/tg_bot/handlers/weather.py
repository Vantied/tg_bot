from aiogram import Router, html
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiohttp import ClientSession

from tg_bot.core.constants import (
    ASK_CITY_MESSAGE,
    CITY_NOT_FOUND_MESSAGE,
    WEATHER_REQUEST_ERROR_MESSAGE,
)
from tg_bot.services.weather_api import (
    WeatherRequestError,
    find_city,
    get_weather_text,
)

weather_router = Router(name=__name__)


@weather_router.message(Command('weather'))
async def weather_handler(
    message: Message,
    command: CommandObject,
    http_session: ClientSession,
) -> None:
    """Погода в городе: /weather Омск."""
    query = (command.args or '').strip()
    if not query:
        await message.answer(ASK_CITY_MESSAGE)
        return
    try:
        city = await find_city(http_session, query)
        if city is None:
            await message.answer(
                CITY_NOT_FOUND_MESSAGE.format(city=html.quote(query)),
            )
            return
        text = await get_weather_text(http_session, city)
    except WeatherRequestError:
        await message.answer(WEATHER_REQUEST_ERROR_MESSAGE)
        return
    await message.answer(text)
