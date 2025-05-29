import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Callable, ContextManager
from contextlib import contextmanager
from typing import Any, Optional, Callable, TypeVar

T = TypeVar("T")  # For generic type hints


class FileCache:
    def __init__(self, cache_dir: str = "~/.agentic/cache"):
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self.cache_dir / f"{safe_key}.pickle"

    def get(
        self,
        key: str,
        fetch_fn: Optional[Callable[[], T]] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Optional[T]:
        """
        Retrieve item from cache or fetch and cache it if not found.

        Args:
            key: Cache key
            fetch_fn: Function to call to fetch data if not in cache
            ttl: Time to live in seconds (optional)

        Returns:
            Cached value or newly fetched value if fetch_fn provided,
            None if no cache hit and no fetch_fn provided
        """
        cache_path = self._get_cache_path(key)

        # Try to get from cache first
        if cache_path.exists():
            try:
                with open(cache_path, "rb") as f:
                    timestamp, data = pickle.load(f)

                if ttl_seconds is not None:
                    age = (datetime.now() - timestamp).total_seconds()
                    if age <= ttl_seconds:
                        return data
                    cache_path.unlink()  # Remove expired cache
                else:
                    return data

            except (pickle.PickleError, EOFError):
                pass

        # If we get here, either:
        # - Cache doesn't exist
        # - Cache is expired
        # - Cache is corrupted
        if fetch_fn is None:
            return None

        # Fetch fresh data
        data = fetch_fn()

        # Cache the fresh data
        try:
            with open(cache_path, "wb") as f:
                pickle.dump((datetime.now(), data), f)
        except (pickle.PickleError, OSError) as e:
            print(f"Failed to cache {key}: {e}")

        return data

    def set(self, key: str, value: Any) -> None:
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "wb") as f:
                pickle.dump((datetime.now(), value), f)
        except (pickle.PickleError, OSError) as e:
            print(f"Failed to cache {key}: {e}")
            raise RuntimeError(f"Can't pickled object to cache, key {key}")

    @contextmanager
    def cached(self, key: str, ttl: Optional[int] = None) -> ContextManager[Any]:
        """
        Context manager that returns cached data if available,
        otherwise executes the block and caches its return value.

        Args:
            key: Cache key
            ttl: Time to live in seconds (optional)

        Usage:
            with cache.cached("my_key") as data:
                if data is None:
                    # This block only runs if cache miss
                    data = expensive_operation()
                    return data  # This gets cached
        """
        data = self.get(key, ttl)
        try:
            yield data
        except StopIteration as e:
            # Capture the return value from the with block
            data = e.value
            self.set(key, data)
        except Exception:
            raise


file_cache = FileCache()
