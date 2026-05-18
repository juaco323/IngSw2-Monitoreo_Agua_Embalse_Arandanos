from contextvars import ContextVar
from typing import Optional
from uuid import UUID, uuid4

_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


def set_correlation_id(value: Optional[str]) -> None:
    _correlation_id.set(value)


def get_correlation_id() -> Optional[str]:
    return _correlation_id.get()


def ensure_correlation_id() -> str:
    current = _correlation_id.get()
    if current:
        return current
    new_id = str(uuid4())
    _correlation_id.set(new_id)
    return new_id


def parse_correlation_id(value: Optional[str]) -> Optional[UUID]:
    if not value:
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None
