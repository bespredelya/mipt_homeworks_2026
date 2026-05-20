from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from gigavibe.config import AppConfig


class LlmError(RuntimeError):
    pass


class LlmClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        try:
            from openai import OpenAI
        except ImportError as error:
            raise LlmError(
                'Не установлена библиотека openai. Выполните: pip install -r requirements.txt'
            ) from error

        self._client = OpenAI(api_key=config.api_key, base_url=config.api_host)

    def complete(self, messages: list[dict[str, str]]) -> str:
        if self._config.stream:
            return self._complete_stream(messages)
        return self._complete_plain(messages)

    def _complete_plain(self, messages: list[dict[str, str]]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self._config.model,
                messages=cast(Any, messages),
                temperature=self._config.temperature,
            )
        except Exception as error:
            raise LlmError(f'Ошибка запроса к модели: {error}') from error

        content = response.choices[0].message.content
        return content or ''

    def _complete_stream(self, messages: list[dict[str, str]]) -> str:
        try:
            stream = self._client.chat.completions.create(
                model=self._config.model,
                messages=cast(Any, messages),
                temperature=self._config.temperature,
                stream=True,
            )
            return collect_stream(stream)
        except KeyboardInterrupt:
            raise
        except Exception as error:
            raise LlmError(f'Ошибка запроса к модели: {error}') from error


def collect_stream(stream: Iterable[Any]) -> str:
    parts: list[str] = []
    for event in stream:
        delta = event.choices[0].delta
        content = getattr(delta, 'content', None)
        if content:
            print(content, end='', flush=True)
            parts.append(content)
    print()
    return ''.join(parts)
