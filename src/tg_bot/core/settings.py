from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие настройки
    token: str

    # Настройки подключения к БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_server: str
    postgres_port: int

    # Нейросеть для /late. Любой сервис с OpenAI-совместимым API
    # (OpenRouter, DeepSeek, OpenCode Zen): меняются только эти три поля.
    # Без ключа команда /late отвечает, что функция не настроена.
    llm_api_key: str | None = None
    llm_base_url: str = 'https://openrouter.ai/api/v1'
    llm_model: str = 'google/gemma-4-31b-it:free'
    # Запасные модели через запятую: пробуются по очереди, если основная
    # перегружена (429), недоступна или на ней кончились деньги (402).
    # Пусто - без запасных.
    llm_fallback_models: str = 'google/gemma-4-26b-a4b-it:free'
    # Выключать «рассуждения» у моделей, которые думают перед ответом:
    # для отмазки они не нужны и съедают весь лимит токенов. Параметр
    # понимает OpenRouter; для API, где его нет (DeepSeek напрямую), - false.
    llm_disable_reasoning: bool = True

    @property
    def llm_models(self) -> list[str]:
        """Основная модель и запасные, без повторов, в порядке попыток."""
        fallbacks = [m.strip() for m in self.llm_fallback_models.split(',')]
        models = [self.llm_model, *fallbacks]
        return [m for i, m in enumerate(models) if m and m not in models[:i]]

    @property
    def db_url(self) -> str:
        """Строка подключения к БД."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
