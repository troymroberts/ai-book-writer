from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from pydantic_settings import BaseSettings
from pydantic import (
    Field,
    HttpUrl,
    SecretStr,
    validator,
    model_validator,
    ValidationError,
    field_serializer
)
from pydantic_settings import SettingsConfigDict
from typing import Literal, Optional, Union
import re
from .environments import EnvironmentSettings, detect_environment, get_environment_settings

class LLMSettings(BaseSettings):
    """Configuration for LLM providers and models"""

    @field_serializer('openai_api_key', 'deepseek_api_key', 'gemini_api_key', 'groq_api_key', 'o1_api_key', 'gemini_flash_api_key')
    def serialize_secrets(self, value: Union[SecretStr, None]) -> Union[str, None]:
        """Serialize SecretStr fields for JSON compatibility"""
        return value.get_secret_value() if value else None

    model: Optional[Literal[
        'mistral-nemo-instruct-2407',
        'openai/gpt-4',
        'openai/gpt-3.5-turbo',
        'deepseek/deepseek-chat',
        'deepseek/deepseek-reasoner',
        'deepseek-chat',
        'gemini/gemini-pro',
        'groq/llama2-70b-4096',
        'gemini-flash/gemini-flash',
        'ollama/llama2',
        'ollama/mistral',
        'ollama/codellama',
        'ollama/deepseek-r1-1.5b'
        'ollama/deepseek-r1-14b'
        'ollama/deepseek-r1-32b'
    ]] = Field(default=None, description="Selected LLM model")

    ollama_base_url: Optional[str] = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama API"
    )

    openai_api_key: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key"
    )

    deepseek_api_key: Optional[SecretStr] = Field(
        default=None,
        description="DeepSeek API key"
    )

    deepseek_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for DeepSeek API"
    )

    gemini_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Gemini API key"
    )

    groq_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Groq API key"
    )

    o1_api_key: Optional[SecretStr] = Field(
        default=None,
        description="O1 API key"
    )

    gemini_flash_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Gemini Flash API key"
    )

    mistral_nemo_base_url: Optional[str] = Field(
        default=None,
        description="Base URL for local Mistral-Nemo model"
    )

    test_connection: bool = Field(
        default=True,
        description="Enable connection testing on startup"
    )

    connection_timeout: int = Field(
        default=30,
        description="Connection timeout in seconds",
        ge=5,
        le=300
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_llm_config(self) -> dict:
        """Get LLM configuration in dictionary format

        Returns:
            dict: Configuration dictionary with model and API key
        """
        config = {
            "model": self.model,
            "api_key": None,
            "base_url": None
        }

        if "openai" in self.model and self.openai_api_key:
            config["api_key"] = self.openai_api_key.get_secret_value()
        elif "deepseek" in self.model and self.deepseek_api_key:
            config["api_key"] = self.deepseek_api_key.get_secret_value()
            if self.deepseek_base_url:
                config["base_url"] = str(self.deepseek_base_url)
        elif "gemini" in self.model and self.gemini_api_key:
            config["api_key"] = self.gemini_api_key.get_secret_value()
        elif "groq" in self.model and self.groq_api_key:
            config["api_key"] = self.groq_api_key.get_secret_value()
        elif "mistral" in self.model and self.mistral_nemo_base_url:
            config["base_url"] = str(self.mistral_nemo_base_url)
        elif "ollama" in self.model and self.ollama_base_url:
             config["base_url"] = str(self.ollama_base_url)


        return config

class GenerationSettings(BaseSettings):
    """Configuration for book generation parameters"""

    output_dir: str = Field(
        default="./book_output", # Corrected default output directory
        description="Directory for generated books"
    )

    max_tokens: int = Field(
        default=4096,
        description="Maximum length of generated text",
        ge=512,
        le=8192
    )

    temperature: float = Field(
        default=0.7,
        description="Controls creativity (0.0-1.0)",
        ge=0.0,
        le=1.0
    )

    max_chapters: int = Field(
        default=10,
        description="Maximum number of chapters per book",
        ge=1,
        le=50
    )

    min_chapter_length: int = Field(
        default=2000,
        description="Minimum words per chapter",
        ge=500,
        le=10000
    )

    max_chapter_length: int = Field(
        default=5000,
        description="Maximum words per chapter",
        ge=1000,
        le=20000
    )

    model_config = SettingsConfigDict(
        env_prefix="GEN_",
        extra="ignore"
    )

class LoggingSettings(BaseSettings):
    """Configuration for application logging"""

    level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )

    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

    file: Optional[str] = Field(
        default=None,
        description="Path to log file (if file logging is desired)"
    )

    model_config = SettingsConfigDict(
        env_prefix="LOG_",
        extra="ignore"
    )

class Settings(BaseSettings):
    """Main application settings

    Attributes:
        llm: Configuration for LLM providers and models
        generation: Configuration for book generation parameters
        environment: Environment-specific settings
        logging: Configuration for application logging
    """

    llm: LLMSettings = Field(default_factory=LLMSettings)
    generation: GenerationSettings = Field(default_factory=GenerationSettings)
    environment: EnvironmentSettings = Field(default_factory=lambda: get_environment_settings())
    logging: LoggingSettings = Field(default_factory=LoggingSettings) # Added LoggingSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        extra="ignore"
    )

    @model_validator(mode='before')
    def validate_required_keys(cls, values):
        """Validate that required API keys are present based on selected model"""
        llm = values.get('llm', {})
        if not llm:
            return values

        # Handle both dictionary and object access
        model_name = llm.get('model') if isinstance(llm, dict) else llm.model
        if not model_name:
            return values

        # Determine provider type from model name or config
        provider_type = None
        if model_name.startswith("openai/"): provider_type = "openai"
        elif model_name.startswith("deepseek/"): provider_type = "deepseek"
        elif model_name.startswith("gemini/"): provider_type = "gemini"
        elif model_name.startswith("groq/"): provider_type = "groq"
        elif model_name.startswith("ollama/"): provider_type = "ollama" # Added Ollama check

        if provider_type == "openai" and not (llm.get('openai_api_key') if isinstance(llm, dict) else llm.openai_api_key):
            raise ValueError("OpenAI API key is required for OpenAI models")
        elif provider_type == "deepseek" and not (llm.get('deepseek_api_key') if isinstance(llm, dict) else llm.deepseek_api_key):
            raise ValueError("DeepSeek API key is required for DeepSeek models")
        elif provider_type == "gemini" and not (llm.get('gemini_api_key') if isinstance(llm, dict) else llm.gemini_api_key):
            raise ValueError("Gemini API key is required for Gemini models")
        elif provider_type == "groq" and not (llm.get('groq_api_key') if isinstance(llm, dict) else llm.groq_api_key):
            raise ValueError("Groq API key is required for Groq models")
        if "mistral" in model_name and not (llm.get('mistral_nemo_base_url') if isinstance(llm, dict) else llm.mistral_nemo_base_url):
            raise ValueError("Mistral Nemo base URL is required for Mistral models")

        return values

    def get_llm_config(self) -> dict:
        """Get LLM configuration in dictionary format

        Returns:
            dict: Configuration dictionary with model and API key
        """
        config = {
            "model": self.llm.model,
            "api_key": None,
            "base_url": None
        }

        if "openai" in self.llm.model and self.llm.openai_api_key:
            config["api_key"] = self.llm.openai_api_key.get_secret_value()
        elif "deepseek" in self.llm.model and self.llm.deepseek_api_key:
            config["api_key"] = self.llm.deepseek_api_key.get_secret_value()
            if self.llm.deepseek_base_url:
                config["base_url"] = str(self.llm.deepseek_base_url)
        elif "gemini" in self.llm.model and self.llm.gemini_api_key:
            config["api_key"] = self.llm.gemini_api_key.get_secret_value()
        elif "groq" in self.llm.model and self.llm.groq_api_key:
            config["api_key"] = self.llm.groq_api_key.get_secret_value()
        elif "mistral" in self.llm.model and self.llm.mistral_nemo_base_url:
            config["base_url"] = str(self.llm.mistral_nemo_base_url)
        elif "ollama" in self.llm.model and self.llm.ollama_base_url: # Added Ollama base_url config
             config["base_url"] = str(self.llm.ollama_base_url)


        return config


def get_settings() -> Settings:
    """Factory function to get settings instance

    Returns:
        Settings: Configured settings instance
    """
    return Settings()