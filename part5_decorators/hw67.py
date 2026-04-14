import json
from typing import Any, ParamSpec, Protocol, TypeVar
from datetime import UTC, datetime
from urllib.request import urlopen
from functools import wraps

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
        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on
        self._count_fail = 0
        self._last_block_time = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(UTC)
            full_exception = f"{func.__module__}.{func.__name__}"
            if self._last_block_time is not None:
                difference = (now - self._last_block_time).total_seconds()
                if difference < self._time_to_recover:
                    raise BreakerError(func_name=full_exception, block_time=self._last_block_time)
                self._last_block_time = None
                self._count_fail = 0
            try:
                result = func(*args, **kwargs)
            except self._triggers_on as error:
                self._count_fail += 1
                if self._count_fail >= self._critical_count:
                    self._last_block_time = datetime.now(UTC)
                    raise BreakerError(func_name=full_exception, block_time=self._last_block_time) from error
                raise error
            else:
                self._count_fail = 0
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