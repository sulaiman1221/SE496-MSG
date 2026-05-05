"""Security regression tests."""

import pytest
from pydantic import ValidationError

from msg.config import Settings


# F-11: Settings must reject missing or short secrets at boot.


class TestF11RequiredSecrets:
    """Settings must refuse to build when a required secret is missing or short."""

    _GOOD = {
        "OPENAI_API_KEY": "sk-test-1234567890",
        "SUPABASE_URL": "http://test.local",
        "SUPABASE_ANON_KEY": "anon-key-1234567890",
        "SUPABASE_SERVICE_KEY": "service-key-1234567890",
    }

    def test_all_secrets_present_succeeds(self):
        settings = Settings(**self._GOOD)
        assert settings.supabase_service_key == "service-key-1234567890"

    @pytest.mark.parametrize(
        "missing_field",
        [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_KEY",
        ],
    )
    def test_empty_secret_rejected(self, missing_field, monkeypatch):
        # Stop pydantic-settings from picking up a real .env file.
        monkeypatch.delenv(missing_field, raising=False)
        kwargs = dict(self._GOOD)
        kwargs[missing_field] = ""
        with pytest.raises(ValidationError):
            Settings(**kwargs)

    @pytest.mark.parametrize(
        "short_field",
        [
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_KEY",
        ],
    )
    def test_too_short_secret_rejected(self, short_field, monkeypatch):
        monkeypatch.delenv(short_field, raising=False)
        kwargs = dict(self._GOOD)
        kwargs[short_field] = "x"
        with pytest.raises(ValidationError):
            Settings(**kwargs)
