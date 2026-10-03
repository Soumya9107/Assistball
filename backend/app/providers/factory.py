from typing import Dict, Optional, Type
from app.config import settings
from app.providers.base import ProviderError, VisionProvider
from app.providers.claude import ClaudeProvider
from app.providers.gemini import GeminiProvider
from app.providers.mock import MockProvider
from app.providers.openai_provider import OpenAIProvider

# Registry mapping provider names to provider classes
PROVIDER_REGISTRY: Dict[str, Type[VisionProvider]] = {
    "claude": ClaudeProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "mock": MockProvider,
}


def register_provider(name: str, provider_cls: Type[VisionProvider]) -> None:
    """Utility to register a new VisionProvider dynamically."""
    PROVIDER_REGISTRY[name.lower()] = provider_cls


def get_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> VisionProvider:
    """
    Factory function to instantiate the configured VisionProvider.

    Args:
        provider_name: Optional provider name override ('claude', 'openai', 'gemini').
        model_name: Optional model name override.

    Returns:
        Instance of VisionProvider subclass.

    Raises:
        ProviderError: If the provider is unsupported or invalid.
    """
    target_provider = (provider_name or settings.PROVIDER or "claude").lower()
    target_model = model_name or settings.MODEL_NAME

    if target_provider not in PROVIDER_REGISTRY:
        raise ProviderError(
            400,
            f"Unsupported provider '{target_provider}'. Supported providers are: {', '.join(PROVIDER_REGISTRY.keys())}.",
        )

    provider_cls = PROVIDER_REGISTRY[target_provider]
    return provider_cls(model_name=target_model)
