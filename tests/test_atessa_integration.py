"""Tests for Atessa LLM provider integration."""

import os
from unittest.mock import patch

import pytest

from tradingagents.llm_clients.api_key_env import get_api_key_env
from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.llm_clients.model_catalog import get_known_models, get_model_options
from tradingagents.llm_clients.validators import validate_model


class TestAtessaIntegration:
    """Test suite for Atessa provider configuration."""

    def test_atessa_api_key_env_mapping(self):
        """Verify Atessa maps to ATESSA_API_KEY."""
        assert get_api_key_env("atessa") == "ATESSA_API_KEY"

    def test_atessa_in_known_models(self):
        """Verify Atessa appears in the model catalog."""
        known_models = get_known_models()
        assert "atessa" in known_models
        assert len(known_models["atessa"]) > 0

    def test_atessa_quick_models_configured(self):
        """Verify quick thinking models are available for Atessa."""
        quick_models = get_model_options("atessa", "quick")
        assert len(quick_models) > 0
        # Verify specific fast models are present
        model_ids = [model_id for _, model_id in quick_models]
        assert "gpt-5.4-mini" in model_ids
        assert "claude-haiku-4.5" in model_ids
        assert "custom" in model_ids

    def test_atessa_deep_models_configured(self):
        """Verify deep thinking models are available for Atessa."""
        deep_models = get_model_options("atessa", "deep")
        assert len(deep_models) > 0
        # Verify specific powerful models are present
        model_ids = [model_id for _, model_id in deep_models]
        assert "claude-opus-4-7" in model_ids
        assert "gpt-5.5" in model_ids
        assert "custom" in model_ids

    def test_atessa_model_validation(self):
        """Verify Atessa models pass validation."""
        # Test a few key models from different providers
        test_models = [
            "gpt-5.4-mini",
            "claude-opus-4-7",
            "gemini-3.1-pro",
            "deepseek-v4-flash",
        ]
        for model in test_models:
            with self.subTest(model=model):
                assert validate_model("atessa", model)

    @patch.dict(os.environ, {"ATESSA_API_KEY": "sk-proxy-test-key"})
    def test_atessa_client_creation(self):
        """Verify Atessa uses OpenAI-compatible client with correct base URL."""
        client = create_llm_client("atessa", "gpt-5.4-mini")

        # Should create an OpenAI client
        from tradingagents.llm_clients.openai_client import OpenAIClient
        assert isinstance(client, OpenAIClient)

        # Should use Atessa base URL
        assert client.base_url == "https://atessa.top/v1"

        # Should have correct model
        assert client.model == "gpt-5.4-mini"

    @patch.dict(os.environ, {"ATESSA_API_KEY": "sk-proxy-test-key"})
    def test_atessa_client_with_different_models(self):
        """Verify Atessa client works with models from different providers."""
        test_cases = [
            ("gpt-5.5", "OpenAI model"),
            ("claude-sonnet-4-6", "Anthropic model"),
            ("gemini-3.5-flash", "Google model"),
            ("kimi-k2.6", "Moonshot model"),
        ]

        for model, description in test_cases:
            with self.subTest(model=model, description=description):
                client = create_llm_client("atessa", model)
                assert client.model == model
                assert client.base_url == "https://atessa.top/v1"

    def test_atessa_provider_name(self):
        """Verify Atessa client returns correct provider name."""
        with patch.dict(os.environ, {"ATESSA_API_KEY": "sk-proxy-test"}):
            client = create_llm_client("atessa", "gpt-5.4-mini")
            assert client.get_provider_name() == "atessa"


@pytest.mark.integration
class TestAtessaCLIIntegration:
    """Test Atessa integration with CLI provider selection."""

    def test_atessa_in_provider_list(self):
        """Verify Atessa appears in CLI provider dropdown."""
        from cli.utils import select_llm_provider
        import inspect

        # Get the source code of select_llm_provider function
        source = inspect.getsource(select_llm_provider)

        # Verify Atessa is in the PROVIDERS list
        assert '"atessa"' in source.lower() or "'atessa'" in source.lower()
        assert "atessa.top" in source.lower()
