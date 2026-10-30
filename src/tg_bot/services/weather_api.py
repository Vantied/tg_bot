from dataclasses import dataclass
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import aiohttp

from tg_bot.core.constants import (
    GEOCODING_API_URL,
    TIMEOUT,
    UNKNOWN_WEATHER,
    WEATHER_API_URL,
    WEATHER_CODES,
    WEATHER_CURRENT_FIELDS,
    WEATHER_MESSAGE,
)


class WeatherRequestError(Exception):
    """Сервис погоды не ответил или ответил ошибкой."""


@dataclass(frozen=True)
class City:
    """Найденный город."""

    name: str
    latitude: float
    longitude: float
    # Часовой пояс IANA, например 'Asia/Omsk'. None - сервис не прислал
    # пояс или прислал такой, которого нет в базе tzdata.
    timezone: str | None


async def find_city(
    http_session: aiohttp.ClientSession,
    query: str,
) -> City | None:
    """Ищет город по названию. None - не найден."""
    data = await get_json(
        http_session,
        GEOCODING_API_URL,
        {'name': query, 'count': 1, 'language': 'ru', 'format': 'json'},
    )
    results = data.get('results') or []
    if not results:
        return None
    first = results[0]
    name = ', '.join(
        part for part in (first.get('name'), first.get('country')) if part
    )
    return City(
        name=name,
        latitude=first['latitude'],
        longitude=first['longitude'],
        timezone=valid_timezone(first.get('timezone')),
    )


def valid_timezone(name: object) -> str | None:
    """Возвращает название пояса, если zoneinfo его знает."""
    if not isinstance(name, str):
        return None
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return None
    return name


async def get_weather_text(
    http_session: aiohttp.ClientSession,
    city: City,
) -> str:
    """Текущая погода в городе в виде готового сообщения."""
    data = await get_json(
        http_session,
        WEATHER_API_URL,
        {
            'latitude': city.latitude,
            'longitude': city.longitude,
            'current': WEATHER_CURRENT_FIELDS,
            'wind_speed_unit': 'ms',
            'timezone': 'auto',
        },
    )
    try:
        current = data['current']
        emoji, description = WEATHER_CODES.get(
            current['weather_code'],
            UNKNOWN_WEATHER,
        )
        return WEATHER_MESSAGE.format(
            city=city.name,
            emoji=emoji,
            description=description,
            temperature=round(current['temperature_2m']),
            feels_like=round(current['apparent_temperature']),
            wind=round(current['wind_speed_10m']),
        )
    except (KeyError, TypeError) as error:
        raise WeatherRequestError from error


async def get_json(
    http_session: aiohttp.ClientSession,
    url: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """GET-запрос с таймаутом. Любая сетевая ошибка - WeatherRequestError."""
    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    try:
        async with http_session.get(
            url,
            params=params,
            timeout=timeout,
        ) as response:
            response.raise_for_status()
            data = await response.json()
    except (TimeoutError, aiohttp.ClientError) as error:
        raise WeatherRequestError from error
    if not isinstance(data, dict):
        raise WeatherRequestError
    return data
