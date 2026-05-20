from __future__ import annotations

import os


def clear_screen() -> None:
    command = 'cls' if os.name == 'nt' else 'clear'
    os.system(command)


def print_error(message: str) -> None:
    print(f'Ошибка: {message}')
