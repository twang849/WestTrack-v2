import pytest
import time
from pathlib import Path
from typing import Any
import shutil
import pickle
from datetime import datetime

from agentic.file_cache import FileCache  # Assuming the class is in cache.py


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create a temporary cache directory for testing."""
    cache_dir = tmp_path / ".agentic" / "cache"
    cache_dir.mkdir(parents=True)
    yield cache_dir
    # Cleanup after tests
    shutil.rmtree(cache_dir)


@pytest.fixture
def cache(temp_cache_dir):
    """Create a FileCache instance with temporary directory."""
    return FileCache(str(temp_cache_dir))


def test_cache_initialization(temp_cache_dir):
    """Test cache directory is created properly."""
    cache = FileCache(str(temp_cache_dir))
    assert temp_cache_dir.exists()
    assert temp_cache_dir.is_dir()


def test_basic_cache_operations(cache):
    """Test basic set and get operations."""
    # Test setting and getting a simple value
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"

    # Test getting non-existent key
    assert cache.get("nonexistent_key") is None


def test_cache_with_fetch_function(cache):
    """Test get operation with fetch function."""
    call_count = 0

    def fetch_data():
        nonlocal call_count
        call_count += 1
        return "fetched_value"

    # First call should fetch
    result1 = cache.get("fetch_key", fetch_data)
    assert result1 == "fetched_value"
    assert call_count == 1

    # Second call should use cache
    result2 = cache.get("fetch_key", fetch_data)
    assert result2 == "fetched_value"
    assert call_count == 1  # Fetch function not called again


def test_cache_ttl(cache):
    """Test TTL functionality."""

    def fetch_data():
        return "ttl_test_value"

    # Store with 1 second TTL
    result1 = cache.get("ttl_key", fetch_data, ttl_seconds=1)
    assert result1 == "ttl_test_value"

    # Immediate fetch should use cache
    result2 = cache.get("ttl_key", fetch_data, ttl_seconds=1)
    assert result2 == "ttl_test_value"

    # Wait for TTL to expire
    time.sleep(1.1)

    # Should fetch fresh data
    result3 = cache.get("ttl_key", fetch_data, ttl_seconds=1)
    assert result3 == "ttl_test_value"

    # Verify cache file was recreated
    cache_path = cache._get_cache_path("ttl_key")
    assert cache_path.exists()


def test_cache_with_complex_data(cache):
    """Test caching of complex Python objects."""
    complex_data = {
        "string": "value",
        "number": 42,
        "list": [1, 2, 3],
        "dict": {"nested": "data"},
        "tuple": (1, "two", 3.0),
    }

    cache.set("complex_key", complex_data)
    retrieved_data = cache.get("complex_key")
    assert retrieved_data == complex_data
    assert isinstance(retrieved_data["tuple"], tuple)  # Check type preservation


def test_safe_key_generation(cache):
    """Test that unsafe characters in keys are handled properly."""
    unsafe_key = "test/unsafe:#key!@"
    cache.set(unsafe_key, "value")

    # Verify we can retrieve the value
    assert cache.get(unsafe_key) == "value"

    # Verify the filename is safe
    cache_path = cache._get_cache_path(unsafe_key)
    assert "/" not in str(cache_path.name)
    assert ":" not in str(cache_path.name)
    assert cache_path.exists()


def test_corrupted_cache_handling(cache, temp_cache_dir):
    """Test handling of corrupted cache files."""
    # Create a corrupted cache file
    corrupted_path = cache._get_cache_path("corrupted_key")
    with open(corrupted_path, "wb") as f:
        f.write(b"corrupted data")

    # Should return None for corrupted data
    assert cache.get("corrupted_key") is None

    # Should be able to fetch and store new data
    def fetch_data():
        return "fresh_data"

    result = cache.get("corrupted_key", fetch_data)
    assert result == "fresh_data"


def test_concurrent_access(cache):
    """Test cache behavior with concurrent access simulation."""
    from concurrent.futures import ThreadPoolExecutor
    import random

    def worker(i: int) -> str:
        key = f"concurrent_key_{i % 5}"  # Use 5 different keys

        def fetch():
            time.sleep(random.uniform(0.01, 0.05))  # Simulate work
            return f"value_{i}"

        return cache.get(key, fetch)

    # Run multiple concurrent operations
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(worker, range(50)))

    assert len(results) == 50
    assert all(isinstance(r, str) for r in results)


def test_error_handling(cache):
    """Test error handling in cache operations."""

    class UnpickleableObject:
        def __reduce__(self):
            raise pickle.PickleError("Cannot pickle this")

    # Test unpickleable object
    with pytest.raises(Exception):
        cache.set("unpickleable", UnpickleableObject())

    # Test fetch function raising exception
    def failing_fetch():
        raise ValueError("Fetch failed")

    with pytest.raises(ValueError):
        cache.get("failing_key", failing_fetch)
