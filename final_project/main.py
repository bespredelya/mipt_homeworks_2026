from __future__ import annotations

from gigavibe.cli import ChatApp
from gigavibe.config import ConfigError, load_config
from gigavibe.console import print_error
from gigavibe.llm import LlmClient, LlmError


def main() -> None:
    try:
        config = load_config()
        client = LlmClient(config)
    except (ConfigError, LlmError) as error:
        print_error(str(error))
        return

    ChatApp(config, client).run()


if __name__ == '__main__':
    main()
