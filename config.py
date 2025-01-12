from typing import Dict, Any
from config.settings import get_settings
import os

# Genre configuration
#genre_template = "config_templates/genre/literary_fiction.py"
os.environ['BOOK_GENRE'] = "genre/literary_fiction"  # Set environment variable for main.py

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
