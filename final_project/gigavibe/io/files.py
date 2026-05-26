
from __future__ import annotations

import re
from pathlib import Path

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
FILE_REFERENCE_RE = re.compile(r'@::(.+?)::')


class FileInsertError(ValueError):
    pass


def expand_file_references(message: str) -> str:

    def replace(match: re.Match[str]) -> str:
        path = Path(match.group(1)).expanduser()
        return f'\n{_read_text_file(path)}'

    return FILE_REFERENCE_RE.sub(replace, message)


def _read_text_file(path: Path) -> str:
    try:
        stat = path.stat()
    except OSError as error:
        raise FileInsertError(f'Не удалось найти файл {path}: {error}') from error

    if not path.is_file():
        raise FileInsertError(f'{path} не является файлом.')
    if stat.st_size > MAX_FILE_SIZE_BYTES:
        raise FileInsertError(f'Файл {path} больше 5 МБ.')

    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError as error:
        raise FileInsertError(f'Файл {path} не похож на UTF-8 текст.') from error
    except OSError as error:
        raise FileInsertError(f'Не удалось прочитать файл {path}: {error}') from error
