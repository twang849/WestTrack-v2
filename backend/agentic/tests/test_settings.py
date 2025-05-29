import pytest
from agentic.settings import Settings  # adjust import path as needed


@pytest.fixture
def settings():
    """Create temporary settings instance for testing"""
    s = Settings(db_path=":memory:")  # use in-memory SQLite database
    yield s
    # cleanup after each test
    for key in s.list_settings():
        s.delete_setting(key)


def test_settings_basic_operations(settings):
    # Test setting and getting values
    settings.set("test_key", "test_value")
    assert settings.get("test_key") == "test_value"

    # Test default value
    assert settings.get("nonexistent", "default") == "default"

    # Test overwriting value
    settings.set("test_key", "new_value")
    assert settings.get("test_key") == "new_value"

    # Test deleting value
    settings.delete_setting("test_key")
    assert settings.get("test_key") is None


def test_settings_list_and_clear(settings):
    # Test listing settings
    settings.set("key1", "value1")
    settings.set("key2", "value2")

    settings_list = settings.list_settings()
    assert len(settings_list) == 2
    assert "key1" in settings_list
    assert "key2" in settings_list
