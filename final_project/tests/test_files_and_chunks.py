from __future__ import annotations

from pathlib import Path

import pytest

from gigavibe.chunks import ChunkOptions, make_chunks, parse_chunk_command
from gigavibe.files import FileInsertError, expand_file_references


def test_expand_file_references(tmp_path: Path) -> None:
    source = tmp_path / 'main.py'
    source.write_text('print(1 / 0)', encoding='utf-8')

    expanded = expand_file_references(f'Что не так? @::{source}::')

    assert expanded == 'Что не так? \nprint(1 / 0)'


def test_expand_file_references_missing_file() -> None:
    with pytest.raises(FileInsertError):
        expand_file_references('@::/no/such/file.txt::')


def test_parse_chunk_command_defaults_to_paragraphs() -> None:
    options = parse_chunk_command('/filechunk paragraph=3 -y')

    assert options.paragraph_count == 3
    assert options.length is None
    assert options.auto is True


def test_parse_chunk_command_rejects_conflicting_modes() -> None:
    with pytest.raises(ValueError):
        parse_chunk_command('/filechunk paragraph=3 len=150')


def test_make_paragraph_chunks() -> None:
    text = 'one\n\ntwo\nthree\n'

    assert make_chunks(text, ChunkOptions(paragraph_count=2)) == ['one\ntwo', 'three']


def test_make_length_chunks() -> None:
    assert make_chunks('abcdef', ChunkOptions(length=2)) == ['ab', 'cd', 'ef']
