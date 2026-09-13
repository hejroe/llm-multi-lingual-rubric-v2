"""Tests for scoring.io's model-digest auto-detection (5.7/9.6): Ollama's
`/api/tags`, GGUF SHA256 hashing, and the backend-dispatch wrapper around
both.
"""

import hashlib
import json
from unittest.mock import MagicMock, patch

from scoring.io import (
    auto_detect_model_digest,
    compute_gguf_digest,
    fetch_ollama_digest,
)


def test_compute_gguf_digest_matches_hashlib(tmp_path):
    gguf_path = tmp_path / "model.gguf"
    gguf_path.write_bytes(b"fake gguf content, several bytes long" * 1000)
    expected = hashlib.sha256(gguf_path.read_bytes()).hexdigest()
    assert compute_gguf_digest(gguf_path) == expected


def test_compute_gguf_digest_missing_file_returns_none(tmp_path):
    assert compute_gguf_digest(tmp_path / "does_not_exist.gguf") is None


def _mock_ollama_response(payload: dict):
    mock_response = MagicMock()
    mock_response.__enter__.return_value = mock_response
    mock_response.read.return_value = json.dumps(payload).encode()
    return mock_response


def test_fetch_ollama_digest_finds_matching_model():
    payload = {
        "models": [
            {"name": "llama3.2:1b", "digest": "abc123"},
            {"name": "qwen3:4b", "digest": "def456"},
        ]
    }
    with patch("urllib.request.urlopen", return_value=_mock_ollama_response(payload)):
        assert fetch_ollama_digest("llama3.2:1b") == "abc123"
        assert fetch_ollama_digest("qwen3:4b") == "def456"


def test_fetch_ollama_digest_no_match_returns_none():
    payload = {"models": [{"name": "other:1b", "digest": "xyz"}]}
    with patch("urllib.request.urlopen", return_value=_mock_ollama_response(payload)):
        assert fetch_ollama_digest("llama3.2:1b") is None


def test_fetch_ollama_digest_unreachable_returns_none_not_raises():
    import urllib.error

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("connection refused"),
    ):
        assert fetch_ollama_digest("llama3.2:1b") is None


def test_auto_detect_dispatches_by_backend(tmp_path):
    gguf_path = tmp_path / "model.gguf"
    gguf_path.write_bytes(b"content")
    expected = hashlib.sha256(b"content").hexdigest()
    assert (
        auto_detect_model_digest("whatever", "llamacpp", gguf_path=gguf_path)
        == expected
    )

    payload = {"models": [{"name": "llama3.2:1b", "digest": "abc123"}]}
    with patch("urllib.request.urlopen", return_value=_mock_ollama_response(payload)):
        assert auto_detect_model_digest("llama3.2:1b", "ollama") == "abc123"

    assert auto_detect_model_digest("x", "unknown") is None
