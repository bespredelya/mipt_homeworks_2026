from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Role = Literal['system', 'user', 'assistant']


@dataclass(slots=True)
class Message:
    role: Role
    content: str

    def as_dict(self) -> dict[str, str]:
        return {'role': self.role, 'content': self.content}
