from __future__ import annotations

from gigavibe.chunks import make_chunks, parse_chunk_command, read_chunk_file
from gigavibe.config import AppConfig
from gigavibe.console import clear_screen, print_error
from gigavibe.files import FileInsertError, expand_file_references
from gigavibe.history import ChatHistory
from gigavibe.llm import LlmClient, LlmError

EXIT_COMMAND = r'\q'


class ChatApp:
    def __init__(self, config: AppConfig, client: LlmClient) -> None:
        self._config = config
        self._client = client
        self._history = ChatHistory(
            limit_message=config.limit_message,
            limit_chars=config.limit_chars,
        )

    def run(self) -> None:
        print('GigaVibeMiptCode. Для выхода введите \\q.')
        while True:
            user_input = input('>>> ').strip()
            if user_input == EXIT_COMMAND:
                return
            if user_input == '/reset':
                self._history.reset()
                clear_screen()
                print('История очищена.')
                continue
            if user_input.startswith(('/filechunk', '/file_chunk')):
                self._run_file_chunk_mode(user_input)
                continue
            if not user_input:
                continue

            self._handle_chat_message(user_input)

    def _handle_chat_message(self, user_input: str) -> None:
        try:
            expanded = expand_file_references(user_input)
        except FileInsertError as error:
            print_error(str(error))
            return

        self._history.add_user_message(expanded)
        messages = self._history.as_openai_messages(self._config.system_prompt)

        try:
            answer = self._client.complete(messages)
        except KeyboardInterrupt:
            print('\nЗапрос прерван. Можно ввести новое сообщение.')
            return
        except LlmError as error:
            print_error(str(error))
            return

        if not self._config.stream:
            print(answer)
        self._history.add_assistant_message(answer)

    def _run_file_chunk_mode(self, command: str) -> None:
        try:
            options = parse_chunk_command(command)
        except ValueError as error:
            print_error(str(error))
            return

        path = input('Введите путь до файла\n>>> ').strip()
        if path == EXIT_COMMAND:
            return
        prompt = input('Принято. Что нужно сделать для каждого фрагмента (User Prompt)?\n>>> ')
        if prompt.strip() == EXIT_COMMAND:
            return

        try:
            chunks = make_chunks(read_chunk_file(path), options)
        except (FileInsertError, ValueError) as error:
            print_error(str(error))
            return

        if not chunks:
            print('Файл не содержит текста для обработки.')
            return

        print('Принято. Начинаю обработку:')
        for index, chunk in enumerate(chunks, start=1):
            if index > 1 and not options.auto:
                next_action = input('>>> ')
                if next_action.strip() == EXIT_COMMAND:
                    return

            messages = self._chunk_messages(prompt, chunk)
            try:
                answer = self._client.complete(messages)
            except KeyboardInterrupt:
                print('\nЗапрос прерван. Возвращаюсь к основному чату.')
                return
            except LlmError as error:
                print_error(str(error))
                return

            if not self._config.stream:
                print(answer)

        print('Обработка файла завершена.')

    def _chunk_messages(self, prompt: str, chunk: str) -> list[dict[str, str]]:
        content = f'{prompt}\n\nТекст фрагмента:\n{chunk}'
        messages = []
        if self._config.system_prompt:
            messages.append({'role': 'system', 'content': self._config.system_prompt})
        messages.append({'role': 'user', 'content': content})
        return messages

