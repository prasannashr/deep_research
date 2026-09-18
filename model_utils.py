"""Shared model configuration for the deep research agents."""

import os
from typing import Literal

from agents import OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv(override=False)
set_tracing_disabled(True)

Provider = Literal["openai", "gemini", "openrouter", "groq", "explabs"]

BASE_URLS = {
    "explabs": "https://api.experientiallabs.ai/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter": "https://openrouter.ai/api/v1",
    "groq": "https://api.groq.com/openai/v1",
}

API_KEY_NAMES = {
    "explabs": "EXPLABS_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "groq": "GROQ_API_KEY",
}

DEFAULT_MODELS = {
    "explabs": "gpt-5.6-luna",
    "openai": "gpt-5.4-mini",
    "gemini": "gemini-3.1-flash-lite",
    "openrouter": "deepseek/deepseek-v4-flash-0731",
    "groq": "openai/gpt-oss-120b",
}

DEFAULT_MODEL_NAME = os.getenv("DEEP_RESEARCH_MODEL", DEFAULT_MODELS["explabs"])


def _provider_for_model(model_name: str) -> Provider:
    """Infer a compatible provider when MODEL_PROVIDER is omitted."""
    if model_name.startswith("deepseek/") or model_name.startswith("moonshotai/"):
        return "openrouter"
    if model_name.startswith("gemini"):
        return "gemini"
    if model_name.startswith("openai/"):
        return "groq"
    return "openai"


def create_model(provider: Provider, model: str | None = None):
    """Create a model accepted by the OpenAI Agents SDK.

    OpenAI models are returned as model names so the SDK can use its native
    Responses API. Other providers use their OpenAI-compatible Chat Completions
    endpoint and are wrapped in OpenAIChatCompletionsModel.
    """
    api_key_name = API_KEY_NAMES[provider]
    api_key = os.getenv(api_key_name)
    if not api_key:
        raise RuntimeError(f"{api_key_name} is not set")

    model_name = model or DEFAULT_MODELS[provider]
    if provider == "openai":
        return model_name

    client = AsyncOpenAI(
        base_url=BASE_URLS[provider],
        api_key=api_key,
    )
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=client,
    )


def create_model_from_env(variable: str = "DEEP_RESEARCH_MODEL"):
    """Create a model from PROVIDER and model environment variables."""
    model_name = os.getenv(variable) or DEFAULT_MODEL_NAME
    provider = os.getenv("DEEP_RESEARCH_PROVIDER", "explabs").lower()
    if provider == "deepseek":
        provider = "openrouter"
    if provider not in API_KEY_NAMES:
        supported = ", ".join(API_KEY_NAMES)
        raise ValueError(f"Unsupported MODEL_PROVIDER={provider!r}; use {supported}")
    return create_model(provider, model_name)
