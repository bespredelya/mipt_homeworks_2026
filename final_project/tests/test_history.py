from __future__ import annotations

from gigavibe.history import ChatHistory


def test_history_trims_old_messages_by_count() -> None:
    history = ChatHistory(limit_message=2, limit_chars=None)

    history.add_user_message('one')
    history.add_assistant_message('two')
    history.add_user_message('three')

    assert [message.content for message in history.messages] == ['two', 'three']


def test_history_trims_old_messages_by_chars() -> None:
    history = ChatHistory(limit_message=None, limit_chars=6)

    history.add_user_message('hello')
    history.add_assistant_message('world')
    history.add_user_message('abc')

    assert [message.content for message in history.messages] == ['abc']

def test_history_trims_old_messages_by_messages() -> None:
    history = ChatHistory(limit_message=2, limit_chars=100)

    history.add_user_message('one')
    history.add_assistant_message('two')
    history.add_user_message('three')

    assert [message.content for message in history.messages] == ['two', 'three']

def test_history_trims_single_large_message_from_left() -> None:
    history = ChatHistory(limit_message=None, limit_chars=4)

    history.add_user_message('abcdef')

    assert history.messages[0].content == 'cdef'


def test_openai_messages_include_system_prompt() -> None:
    history = ChatHistory(limit_message=None, limit_chars=None)
    history.add_user_message('Hi')

    messages = history.as_openai_messages('System')

    assert messages == [
        {'role': 'system', 'content': 'System'},
        {'role': 'user', 'content': 'Hi'},
    ]

