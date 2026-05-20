from __future__ import annotations

from gigavibe.models import Message


class ChatHistory:
    def __init__(self, limit_message: int | None, limit_chars: int | None) -> None:
        self._messages: list[Message] = []
        self._limit_message = limit_message
        self._limit_chars = limit_chars

    @property
    def messages(self) -> list[Message]:
        return list(self._messages)

    def add_user_message(self, content: str) -> None:
        self._messages.append(Message('user', content))
        self._trim()

    def add_assistant_message(self, content: str) -> None:
        self._messages.append(Message('assistant', content))

    def reset(self) -> None:
        self._messages.clear()

    def as_openai_messages(self, system_prompt: str | None) -> list[dict[str, str]]:
        messages = []
        if system_prompt:
            messages.append(Message('system', system_prompt).as_dict())
        messages.extend(message.as_dict() for message in self._messages)
        return messages

    def _trim(self) -> None:
        if self._limit_message is not None:
            while len(self._messages) > self._limit_message:
                self._messages.pop(0)

        if self._limit_chars is None:
            return

        while len(self._messages) > 1 and self._chars_count() > self._limit_chars:
            self._messages.pop(0)

        if self._messages and self._chars_count() > self._limit_chars:
            latest = self._messages[-1]
            latest.content = latest.content[-self._limit_chars :]

    def _chars_count(self) -> int:
        return sum(len(message.content) for message in self._messages)
