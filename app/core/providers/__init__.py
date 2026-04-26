from app.core.providers.base import ExcelProvider
from app.core.providers.local_file import LocalFileProvider
from app.core.providers.microsoft365 import Microsoft365Provider

_PROVIDERS: dict[str, type[ExcelProvider]] = {
    "microsoft365": Microsoft365Provider,
    "local": LocalFileProvider,
}

# Providers that don't require an OAuth access token (frontend can skip login)
_NO_AUTH_PROVIDERS = {"local"}


def get_provider(provider_type: str = "microsoft365") -> ExcelProvider:
    provider_class = _PROVIDERS.get(provider_type)
    if not provider_class:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"Unknown provider type: {provider_type}. Available: {available}")
    return provider_class()


def requires_auth(provider_type: str) -> bool:
    return provider_type not in _NO_AUTH_PROVIDERS
