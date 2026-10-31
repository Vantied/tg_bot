from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiohttp import ClientSession

from tg_bot.core.constants import (
    ASK_CITY_MESSAGE,
    CITY_NOT_FOUND_MESSAGE,
    WEATHER_REQUEST_ERROR_MESSAGE,
)
from tg_bot.core.exceptions import BotValidationError
from tg_bot.handlers.validators import find_city_or_error, validate_city_query
from tg_bot.services.weather_api import WeatherRequestError, get_weather_text

weather_router = Router(name=__name__)


@weather_router.message(Command('weather'))
async def weather_handler(
    message: Message,
    command: CommandObject,
    http_session: ClientSession,
) -> None:
    """Погода в городе: /weather Омск."""
    query = validate_city_query(command.args, empty_error=ASK_CITY_MESSAGE)
    city = await find_city_or_error(
        http_session,
        query,
        not_found=CITY_NOT_FOUND_MESSAGE,
        request_error=WEATHER_REQUEST_ERROR_MESSAGE,
    )
    try:
        text = await get_weather_text(http_session, city)
    except WeatherRequestError as error:
        raise BotValidationError(WEATHER_REQUEST_ERROR_MESSAGE) from error
    await message.answer(text)
