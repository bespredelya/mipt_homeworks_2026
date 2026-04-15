import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."

P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime):
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int,
        time_to_recover: int,
        triggers_on: type[Exception],
    ):
        errors = []
        if not isinstance(critical_count, int) or critical_count <= 0:
            errors.append(ValueError(INVALID_CRITICAL_COUNT))
        if not isinstance(time_to_recover, int) or time_to_recover <= 0:
            errors.append(ValueError(INVALID_RECOVERY_TIME))
        if errors:
            raise ExceptionGroup(VALIDATIONS_FAILED, errors)
        self.critical_count = critical_count
        self.time_to_recover = time_to_recover
        self.triggers_on = triggers_on
        self.count_fail = 0
        self.last_block_time = None

    def is_blocked(self, now: datetime) -> bool:
        if self.last_block_time is None:
            return False
        difference = (now - self.last_block_time).total_seconds()
        return difference < self.time_to_recover

    def reset_if_recovered(self, now: datetime) -> None:
        if self.last_block_time is None:
            return
        if self.is_blocked(now):
            return
        self.last_block_time = None
        self.count_fail = 0

    def raise_blocked(self, func_name: str) -> None:
        raise BreakerError(
            func_name=func_name,
            block_time=self.last_block_time,
        )

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)
            func_name = f"{func.__module__}.{func.__name__}"
            if self.is_blocked(now):
                self.raise_blocked(func_name)
            self.reset_if_recovered(now)
            try:
                result = func(*args, **kwargs)
            except self.triggers_on as error:
                self.count_fail += 1
                if self.count_fail >= self.critical_count:
                    self.last_block_time = now
                    raise BreakerError(
                        func_name=func_name,
                        block_time=self.last_block_time,
                    ) from error
                raise
            self.count_fail = 0
            return result

        return wrapper


circuit_breaker = CircuitBreaker(5, 30, Exception)


# @circuit_breaker
def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    comments = get_comments(1)
