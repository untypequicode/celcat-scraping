"""Cache en mémoire, simple et thread-safe, avec expiration (TTL)."""

import threading
import time
from typing import Any, Optional, Tuple


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if expires_at < time.monotonic():
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: float) -> None:
        if ttl_seconds <= 0:
            return
        with self._lock:
            self._store[key] = (time.monotonic() + ttl_seconds, value)


ics_cache = TTLCache()
