# GigaVibeMiptCode

Консольный ИИ-ассистент на Python для общения с LLM через OpenAI-compatible API.
Поддерживает историю сообщений, ограничение контекста, YAML/env-конфиг,
вставку файлов через `@::path::`, обработку файлов чанками, `/reset`, `\q`
и streaming-вывод ответа.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Настройка

Можно использовать `config.yaml`:

```yaml
api_key: your_key_here
api_host: http://localhost:11434/v1/
model: gemma3:270m
limit_message: 20
limit_chars: 2000
temperature: 0.2
system_prompt: You are an assistant for Python backend development tasks.
stream: true
```

Параметр `stream` указывает нужно ли возвращать ответы в режиме стриминга или нет.

Также можно передать настройки переменными окружения. Они имеют приоритет над YAML:

```bash
export API_KEY=your_key_here
export API_HOST=http://localhost:11434/v1/
export MODEL=gemma3:270m
export LIMIT_CHARS=2000
python main.py
```

## Запуск

```bash
python main.py
```

Команды:

- `\q` — выйти из программы.
- `/reset` — очистить историю и экран.
- `/filechunk`, `/file_chunk` — обработать файл по частям.
- `/filechunk paragraph=3 -y` — обрабатывать по 3 абзаца автоматически.
- `/filechunk len=150` — делить файл на чанки по 150 символов.

Файл можно приложить к обычному сообщению так:

```text
В чем ошибка? @::/path/to/main.py::
```

Максимальный размер вставляемого файла — 5 МБ.

## Tecns

```bash
pytest
ruff check . --config final_project/ruff.toml
mypy .
```

`pytest` генерирует отчет в `htmlcov/`.