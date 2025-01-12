"""Configuration module for AI Book Writer

Provides centralized configuration management with:
- Environment-specific settings
- Validation and documentation
- Type-safe configuration access
"""

from typing import Dict, Any
from .settings import Settings, get_settings

def get_config() -> Dict[str, Any]:
    """Get the complete configuration including model settings
    
    Returns:
        Dict[str, Any]: Configuration dictionary compatible with autogen
    """
    try:
        settings = get_settings()
        return settings.get_llm_config()
    except Exception as e:
        raise RuntimeError(
            "Failed to load configuration. Please check your settings and environment variables"
        ) from e

__all__ = [
    'Settings',
    'get_settings',
    'get_config'
]
