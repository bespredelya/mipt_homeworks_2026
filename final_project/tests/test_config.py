from __future__ import annotations

from pathlib import Path

import pytest

from gigavibe.config import ConfigError, load_config

CONFIG_ENV_KEYS = (
    'API_KEY',
    'API_HOST',
    'MODEL',
    'LIMIT_MESSAGE',
    'LIMIT_CHARS',
    'TEMPERATURE',
    'SYSTEM_PROMPT',
    'STREAM',
)


def clear_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in CONFIG_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_load_config_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        '\n'.join(
            [
                'api_key: yaml-key',
                'api_host: http://localhost:11434/v1/',
                'model: test-model',
                'limit_message: 2',
                'limit_chars: 50',
                'temperature: 0.7',
                'system_prompt: Be concise.',
                'stream: false',
            ]
        ),
        encoding='utf-8',
    )
    clear_config_env(monkeypatch)

    config = load_config(config_path)

    assert config.api_key == 'yaml-key'
    assert config.api_host == 'http://localhost:11434/v1/'
    assert config.model == 'test-model'
    assert config.limit_message == 2
    assert config.limit_chars == 50
    assert config.temperature == 0.7
    assert config.system_prompt == 'Be concise.'
    assert config.stream is False


def test_env_overrides_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        'api_key: yaml-key\napi_host: http://yaml-host/v1/\n',
        encoding='utf-8',
    )
    clear_config_env(monkeypatch)
    monkeypatch.setenv('API_KEY', 'env-key')
    monkeypatch.setenv('API_HOST', 'http://env-host/v1/')
    monkeypatch.setenv('LIMIT_MESSAGE', '5')

    config = load_config(config_path)

    assert config.api_key == 'env-key'
    assert config.api_host == 'http://env-host/v1/'
    assert config.limit_message == 5


def test_missing_sources_raise_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_config_env(monkeypatch)

    with pytest.raises(ConfigError):
        load_config(tmp_path / 'missing.yaml')


def test_invalid_temperature_raise_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_config_env(monkeypatch)
    config_path = tmp_path / 'config.yaml'
    config_path.write_text(
        'api_key: key\napi_host: http://host/v1/\ntemperature: 2\n',
        encoding='utf-8',
    )

    with pytest.raises(ConfigError):
        load_config(config_path)
