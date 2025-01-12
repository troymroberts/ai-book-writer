"""Environment-specific configuration for AI Book Writer

Provides environment detection and configuration presets
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel

class Environment(str, Enum):
    """Available environment types"""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"
    STAGING = "staging"

class EnvironmentSettings(BaseModel):
    """Environment-specific settings"""
    name: Environment
    debug: bool
    log_level: str
    enable_telemetry: bool

def detect_environment() -> Environment:
    """Detect the current environment from environment variables"""
    env = os.getenv("APP_ENV", "development").lower()
    try:
        return Environment(env)
    except ValueError:
        return Environment.DEVELOPMENT

def get_environment_settings(env: Optional[Environment] = None) -> EnvironmentSettings:
    """Get settings for the specified environment"""
    if env is None:
        env = detect_environment()
    
    if env == Environment.PRODUCTION:
        return EnvironmentSettings(
            name=env,
            debug=False,
            log_level="INFO",
            enable_telemetry=True
        )
    elif env == Environment.TEST:
        return EnvironmentSettings(
            name=env,
            debug=True,
            log_level="DEBUG",
            enable_telemetry=False
        )
    elif env == Environment.STAGING:
        return EnvironmentSettings(
            name=env,
            debug=True,
            log_level="INFO",
            enable_telemetry=True
        )
    else:  # Default to development
        return EnvironmentSettings(
            name=Environment.DEVELOPMENT,
            debug=True,
            log_level="DEBUG",
            enable_telemetry=False
        )
