"""aether_core — shared foundation for all Aether services (stdlib + PyYAML only)."""
from .version import VERSION, API_VERSIONS
from .result import ok, err
from .errors import AetherError, IpcError
from .cancellation import CancellationToken, AetherErrorCancelled
from .schema import validate
from .resource_limits import ResourceBudget

__all__ = [
    "VERSION", "API_VERSIONS", "ok", "err",
    "AetherError", "IpcError", "AetherErrorCancelled",
    "CancellationToken", "validate", "ResourceBudget",
]
