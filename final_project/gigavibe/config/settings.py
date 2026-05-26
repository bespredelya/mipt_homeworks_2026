from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AppConfig:
    api_key: str
    api_host: str
    model: str
    limit_message: int | None = None
    limit_chars: int | None = None
    temperature: float = 0.2
    system_prompt: str | None = None
    stream: bool = True


ENV_KEYS = {
    'api_key': 'API_KEY',
    'api_host': 'API_HOST',
    'model': 'MODEL',
    'limit_message': 'LIMIT_MESSAGE',
    'limit_chars': 'LIMIT_CHARS',
    'temperature': 'TEMPERATURE',
    'system_prompt': 'SYSTEM_PROMPT',
    'stream': 'STREAM',
}


def load_config(path: str | Path = 'config.yaml') -> AppConfig:
    config_path = Path(path)
    raw: dict[str, Any] = {}
    yaml_exists = config_path.exists()

    if yaml_exists:
        try:
            loaded = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        except OSError as error:
            raise ConfigError(f'Не удалось прочитать {config_path}: {error}') from error
        except yaml.YAMLError as error:
            raise ConfigError(f'Некорректный YAML в {config_path}: {error}') from error
        if loaded is None:
            raw = {}
        elif isinstance(loaded, dict):
            raw = dict(loaded)
        else:
            raise ConfigError('config.yaml должен содержать словарь настроек.')

    env_found = False
    for key, env_name in ENV_KEYS.items():
        value = os.environ.get(env_name)
        if value is not None:
            raw[key] = value
            env_found = True

    if not yaml_exists and not env_found:
        raise ConfigError(
            'Не найдены настройки: задайте переменные окружения или создайте config.yaml.'
        )

    api_key = _require_str(raw, 'api_key')
    api_host = _require_str(raw, 'api_host')
    model = _optional_str(raw, 'model') or 'gemma3:270m'
    limit_message = _optional_int(raw, 'limit_message', minimum=1)
    limit_chars = _optional_int(raw, 'limit_chars', minimum=1)
    temperature = _optional_float(raw, 'temperature', default=0.2)
    system_prompt = _optional_str(raw, 'system_prompt')
    stream = _optional_bool(raw, 'stream', default=True)

    if not 0 <= temperature <= 1:
        raise ConfigError('temperature должна быть числом от 0 до 1.')

    return AppConfig(
        api_key=api_key,
        api_host=api_host,
        model=model,
        limit_message=limit_message,
        limit_chars=limit_chars,
        temperature=temperature,
        system_prompt=system_prompt,
        stream=stream,
    )


def _require_str(raw: dict[str, Any], key: str) -> str:
    value = _optional_str(raw, key)
    if not value:
        raise ConfigError(f'Не задан обязательный параметр {key}.')
    return value


def _optional_str(raw: dict[str, Any], key: str) -> str | None:
    value = raw.get(key)
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def _optional_int(raw: dict[str, Any], key: str, minimum: int) -> int | None:
    value = raw.get(key)
    if value in (None, ''):
        return None
    try:
        parsed = int(str(value))
    except (TypeError, ValueError) as error:
        raise ConfigError(f'{key} должен быть целым числом.') from error
    if parsed < minimum:
        raise ConfigError(f'{key} должен быть не меньше {minimum}.')
    return parsed


def _optional_float(raw: dict[str, Any], key: str, default: float) -> float:
    value = raw.get(key)
    if value in (None, ''):
        return default
    try:
        return float(str(value))
    except (TypeError, ValueError) as error:
        raise ConfigError(f'{key} должен быть числом.') from error


def _optional_bool(raw: dict[str, Any], key: str, default: bool) -> bool:
    value = raw.get(key)
    if value in (None, ''):
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {'1', 'true', 'yes', 'y', 'on'}:
        return True
    if normalized in {'0', 'false', 'no', 'n', 'off'}:
        return False
    raise ConfigError(f'{key} должен быть boolean-значением.')
