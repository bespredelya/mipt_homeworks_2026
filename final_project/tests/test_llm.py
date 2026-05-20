from __future__ import annotations

from dataclasses import dataclass

import pytest

from gigavibe.llm import collect_stream


@dataclass
class Delta:
    content: str | None


@dataclass
class Choice:
    delta: Delta


@dataclass
class Event:
    choices: list[Choice]


def test_collect_stream_prints_and_returns_content(
    capsys: pytest.CaptureFixture[str],
) -> None:
    stream = [
        Event([Choice(Delta('Hel'))]),
        Event([Choice(Delta(None))]),
        Event([Choice(Delta('lo'))]),
    ]

    result = collect_stream(stream)

    assert result == 'Hello'
    assert capsys.readouterr().out == 'Hello\n'
