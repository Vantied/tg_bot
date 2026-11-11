import logging
import time

import openai
from openai import AsyncOpenAI

from tg_bot.core.constants import (
    EXCUSE_COOLDOWN_SECONDS,
    EXCUSE_MAX_TOKENS,
    EXCUSE_SYSTEM_PROMPT,
    EXCUSE_TEMPERATURE,
    EXCUSE_TIMEOUT,
    EXCUSE_USER_PROMPT,
    EXCUSE_USER_PROMPT_WITH_REASON,
)
from tg_bot.core.settings import settings

logger = logging.getLogger(__name__)


class ExcuseRequestError(Exception):
    """Нейросеть не ответила, ответила ошибкой или пустым текстом."""


class ExcuseRateLimitError(ExcuseRequestError):
    """Все модели из списка ответили 429: перегружены или кончился лимит."""


# Коды ответа, после которых имеет смысл попробовать следующую модель:
# кончились деньги на платную (402), модели нет (404), таймаут (408),
# перегрузка или лимит (429). Плюс любые сбои сервиса (5xx) и сети.
RETRYABLE_STATUS_CODES = {402, 404, 408, 429}
SERVER_ERROR_STATUS = 500
# Параметр OpenRouter: без него «думающие» модели (например, DeepSeek
# v4.1 flash) тратят весь лимит токенов на рассуждения и не дают текста.
REASONING_OFF = {'reasoning': {'enabled': False}}


def is_retryable(error: openai.APIError) -> bool:
    """Поможет ли другая модель, или ошибка в самом запросе/ключе."""
    if isinstance(error, openai.APIConnectionError):
        return True
    if isinstance(error, openai.APIStatusError):
        return (
            error.status_code in RETRYABLE_STATUS_CODES
            or error.status_code >= SERVER_ERROR_STATUS
        )
    return False


def create_llm_client() -> AsyncOpenAI | None:
    """Клиент OpenAI-совместимого API. None - ключ не задан в .env."""
    if not settings.llm_api_key:
        return None
    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=EXCUSE_TIMEOUT,
        # Повторяем не ту же модель, а следующую из списка - см. ниже.
        max_retries=0,
    )


async def generate_excuse(client: AsyncOpenAI, reason: str | None) -> str:
    """Просит нейросеть придумать отмазку, при желании - по поводу.

    Модели из settings.llm_models пробуются по очереди, пока одна
    не ответит. Неверный ключ и другие ошибки запроса не повторяются.
    """
    prompt = (
        EXCUSE_USER_PROMPT_WITH_REASON.format(reason=reason)
        if reason
        else EXCUSE_USER_PROMPT
    )
    all_rate_limited = True
    for model in settings.llm_models:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': EXCUSE_SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt},
                ],
                max_tokens=EXCUSE_MAX_TOKENS,
                temperature=EXCUSE_TEMPERATURE,
                extra_body=REASONING_OFF
                if settings.llm_disable_reasoning
                else None,
            )
        except openai.APIError as error:
            if is_retryable(error):
                logger.warning('Модель %s не ответила: %r', model, error)
                all_rate_limited &= isinstance(error, openai.RateLimitError)
                continue
            # Неверный ключ, плохой запрос и т.п. - другая модель не поможет.
            logger.warning('Нейросеть вернула ошибку: %r', error)
            raise ExcuseRequestError from error
        text = (
            (response.choices[0].message.content or '').strip()
            if response.choices
            else ''
        )
        if text:
            return text
        logger.warning('Модель %s вернула пустой ответ', model)
        all_rate_limited = False
    if all_rate_limited:
        raise ExcuseRateLimitError
    raise ExcuseRequestError


class Cooldown:
    """Не чаще одного раза в EXCUSE_COOLDOWN_SECONDS на пользователя.

    Хранится в памяти процесса: после перезапуска бота сбрасывается,
    для защиты от спама этого достаточно.
    """

    def __init__(self, seconds: int = EXCUSE_COOLDOWN_SECONDS) -> None:
        """Запоминает длительность паузы."""
        self.seconds = seconds
        self._last_used: dict[int, float] = {}

    def seconds_left(self, user_id: int) -> int:
        """Сколько секунд ещё ждать. 0 - можно."""
        last = self._last_used.get(user_id)
        if last is None:
            return 0
        left = self.seconds - (time.monotonic() - last)
        return max(0, round(left))

    def mark_used(self, user_id: int) -> None:
        """Отмечает, что пользователь только что получил отмазку."""
        self._last_used[user_id] = time.monotonic()


excuse_cooldown = Cooldown()
