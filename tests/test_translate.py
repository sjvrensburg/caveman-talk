"""Tests for caveman.translate — mocks the HTTP layer."""

import json
import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest

import caveman.translate as mod
from caveman.prompts import INTENSITIES, compress_user_prompt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(content: str, status_code: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.ok = status_code == 200
    resp.status_code = status_code
    resp.json.return_value = {
        "choices": [{"message": {"content": content}}],
    } if status_code == 200 else {"error": {"message": "bad request"}}
    resp.text = json.dumps(resp.json.return_value)
    return resp


@pytest.fixture(autouse=True)
def _clear_config_cache():
    """Reset the cached config between tests."""
    mod._cached_config = None
    yield
    mod._cached_config = None


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    """Ensure CAVEMAN_API_KEY is always set."""
    monkeypatch.setenv("CAVEMAN_API_KEY", "test-key")


# ---------------------------------------------------------------------------
# _get_config
# ---------------------------------------------------------------------------

class TestGetConfig:
    def test_defaults(self, monkeypatch):
        monkeypatch.delenv("CAVEMAN_API_BASE", raising=False)
        monkeypatch.delenv("CAVEMAN_MODEL", raising=False)
        monkeypatch.delenv("CAVEMAN_TIMEOUT", raising=False)
        api_base, api_key, model, timeout = mod._get_config()
        assert api_base == "https://api.openai.com/v1"
        assert api_key == "test-key"
        assert model == "gpt-4o-mini"
        assert timeout == 60

    def test_custom_env(self, monkeypatch):
        monkeypatch.setenv("CAVEMAN_API_BASE", "http://localhost:11434/v1/")
        monkeypatch.setenv("CAVEMAN_MODEL", "llama3")
        monkeypatch.setenv("CAVEMAN_TIMEOUT", "120")
        api_base, _, model, timeout = mod._get_config()
        assert api_base == "http://localhost:11434/v1"  # trailing slash stripped
        assert model == "llama3"
        assert timeout == 120

    def test_caching(self):
        first = mod._get_config()
        second = mod._get_config()
        assert first is second

    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv("CAVEMAN_API_KEY")
        with pytest.raises(SystemExit):
            mod._get_config()


# ---------------------------------------------------------------------------
# _chat
# ---------------------------------------------------------------------------

class TestChat:
    @patch("caveman.translate.requests.post")
    def test_success(self, mock_post):
        mock_post.return_value = _mock_response("  compressed text  ")
        result = mod._chat("system", "user")
        assert result == "compressed text"

    @patch("caveman.translate.requests.post")
    def test_api_error_raises_runtime_error(self, mock_post):
        mock_post.return_value = _mock_response("", status_code=400)
        with pytest.raises(RuntimeError, match="400"):
            mod._chat("system", "user")

    @patch("caveman.translate.requests.post")
    def test_passes_timeout(self, mock_post, monkeypatch):
        monkeypatch.setenv("CAVEMAN_TIMEOUT", "30")
        mock_post.return_value = _mock_response("ok")
        mod._chat("system", "user")
        _, kwargs = mock_post.call_args
        assert kwargs["timeout"] == 30


# ---------------------------------------------------------------------------
# compress / decompress
# ---------------------------------------------------------------------------

class TestCompress:
    @patch("caveman.translate._chat")
    def test_default_intensity(self, mock_chat):
        mock_chat.return_value = "compressed"
        result = mod.compress("hello world")
        assert result == "compressed"
        system_arg, user_arg = mock_chat.call_args[0]
        assert "hello world" in user_arg

    @patch("caveman.translate._chat")
    def test_intensity_ultra(self, mock_chat):
        mock_chat.return_value = "compressed"
        mod.compress("hello world", intensity="ultra")
        _, user_arg = mock_chat.call_args[0]
        assert "Abbreviate" in user_arg


class TestDecompress:
    @patch("caveman.translate._chat")
    def test_decompress(self, mock_chat):
        mock_chat.return_value = "expanded text"
        result = mod.decompress("compressed stuff")
        assert result == "expanded text"


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

class TestPrompts:
    def test_all_intensities_produce_prompts(self):
        for level in INTENSITIES:
            prompt = compress_user_prompt("test", level)
            assert "test" in prompt

    def test_invalid_intensity_raises(self):
        with pytest.raises(KeyError):
            compress_user_prompt("test", "invalid")


# ---------------------------------------------------------------------------
# CLI entry points
# ---------------------------------------------------------------------------

class TestCLI:
    @patch("caveman.translate.compress", return_value="compressed")
    def test_cli_compress_with_args(self, mock_compress, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["caveman-compress", "hello", "world"])
        mod._cli_compress()
        assert capsys.readouterr().out.strip() == "compressed"

    @patch("caveman.translate.compress", return_value="compressed")
    def test_cli_compress_intensity_flag(self, mock_compress, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["caveman-compress", "-i", "ultra", "hello"])
        mod._cli_compress()
        mock_compress.assert_called_once_with("hello", "ultra")

    @patch("caveman.translate.decompress", return_value="expanded")
    def test_cli_decompress_with_args(self, mock_decompress, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["caveman-decompress", "hello"])
        mod._cli_decompress()
        assert capsys.readouterr().out.strip() == "expanded"

    def test_cli_compress_no_input_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["caveman-compress"])
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        with pytest.raises(SystemExit):
            mod._cli_compress()

    def test_cli_decompress_no_input_exits(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["caveman-decompress"])
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        with pytest.raises(SystemExit):
            mod._cli_decompress()
