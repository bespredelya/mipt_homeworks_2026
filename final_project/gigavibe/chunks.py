from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from gigavibe.files import MAX_FILE_SIZE_BYTES, FileInsertError


@dataclass(frozen=True, slots=True)
class ChunkOptions:
    paragraph_count: int | None = None
    length: int | None = None
    auto: bool = False


def parse_chunk_command(command: str) -> ChunkOptions:
    parts = command.split()
    paragraph_count: int | None = None
    length: int | None = None
    auto = False

    for part in parts[1:]:
        if part == '-y':
            auto = True
        elif part.startswith('paragraph='):
            paragraph_count = _positive_int(part, 'paragraph')
        elif part.startswith('len='):
            length = _positive_int(part, 'len')
        else:
            raise ValueError(f'Неизвестный аргумент: {part}')

    if paragraph_count is not None and length is not None:
        raise ValueError('Нельзя одновременно использовать paragraph и len.')

    return ChunkOptions(paragraph_count=paragraph_count, length=length, auto=auto)


def read_chunk_file(path: str) -> str:
    file_path = Path(path).expanduser()
    try:
        stat = file_path.stat()
    except OSError as error:
        raise FileInsertError(f'Не удалось найти файл {file_path}: {error}') from error

    if not file_path.is_file():
        raise FileInsertError(f'{file_path} не является файлом.')
    if stat.st_size > MAX_FILE_SIZE_BYTES:
        raise FileInsertError(f'Файл {file_path} больше 5 МБ.')

    try:
        return file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError as error:
        raise FileInsertError(f'Файл {file_path} не похож на UTF-8 текст.') from error
    except OSError as error:
        raise FileInsertError(f'Не удалось прочитать файл {file_path}: {error}') from error


def make_chunks(text: str, options: ChunkOptions) -> list[str]:
    if options.length is not None:
        return [
            text[index : index + options.length]
            for index in range(0, len(text), options.length)
        ]

    paragraph_count = options.paragraph_count or 1
    paragraphs = [paragraph.strip() for paragraph in text.splitlines() if paragraph.strip()]
    chunks = []
    for index in range(0, len(paragraphs), paragraph_count):
        chunks.append('\n'.join(paragraphs[index : index + paragraph_count]))
    return chunks


def _positive_int(part: str, name: str) -> int:
    _, raw_value = part.split('=', maxsplit=1)
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(f'{name} должен быть целым числом.') from error
    if value < 1:
        raise ValueError(f'{name} должен быть больше 0.')
    return value
