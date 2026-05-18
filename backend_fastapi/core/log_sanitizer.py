import hashlib
import re
from copy import deepcopy
from typing import Any, Optional

SENSITIVE_KEYS = frozenset({
    "password", "passwd", "token", "access_token", "refresh_token",
    "api_key", "apikey", "authorization", "secret", "bearer",
    "mailersend_api_token", "jwt_secret",
})

BEARER_PATTERN = re.compile(r"Bearer\s+[\w\-.]+", re.IGNORECASE)


def hash_chat_id(chat_id: str) -> str:
    return hashlib.sha256(chat_id.encode("utf-8")).hexdigest()


def sanitize_details(details: Optional[dict]) -> dict:
    if not details:
        return {}

    def _clean(key: Optional[str], value: Any) -> Any:
        if key and key.lower() in SENSITIVE_KEYS:
            return "[REDACTED]"
        if isinstance(value, dict):
            return {k: _clean(k, v) for k, v in value.items()}
        if isinstance(value, list):
            return [_clean(None, v) for v in value]
        if isinstance(value, str) and BEARER_PATTERN.search(value):
            return BEARER_PATTERN.sub("Bearer [REDACTED]", value)
        return value

    return _clean(None, deepcopy(details))
