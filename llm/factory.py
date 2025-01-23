import os
from typing import Dict, Optional
from .mistral_nemo import MistralNemoImplementation
from .litellm_implementations import (
    OpenAIImplementation,
    DeepSeekImplementation,
    GeminiImplementation,
    GroqImplementation,
    OllamaImplementation # <-- Ensure OllamaImplementation is imported
)
from .interface import LLMInterface
from .prompt import PromptConfig
from .register_model_clients import register_deepseek_client
import autogen
from .litellm_base import LiteLLMBase

class LLMFactory:
    """Factory for creating LLM instances"""

    @staticmethod
    def create_llm(config: Dict, prompt_config: Optional[Dict] = None) -> LLMInterface:
        """Create an LLM instance based on configuration

        Args:
            config: Dictionary containing LLM configuration
            prompt_config: Optional dictionary containing prompt template configuration

        Returns:
            Configured LLMInterface instance
        """

        # Validate required configuration
        if not isinstance(config, dict):
            print("❌ Error: Invalid configuration format")
            print("The LLM configuration must be provided as a dictionary")
            exit(1)

        if 'model' not in config:
            print("❌ Error: Missing model configuration")
            print("Please specify a model in your configuration")
            print("Supported models:")
            print("- mistral-nemo-instruct-2407 (local)")
            print("- openai/ (e.g. openai/gpt-4)")
            print("- deepseek/ (e.g. deepseek-chat)")
            print("- gemini/ (e.g. gemini/gemini-pro)")
            print("- groq/ (e.g. groq/llama2-70b)")
            print("- ollama/ (e.g. ollama/llama2)") # <-- Added ollama to supported models list
            exit(1)

        # Validate API key presence based on model type
        model = config['model'].lower()
        if any(model.startswith(prefix) for prefix in ['openai/', 'deepseek/', 'gemini/', 'groq/']):
            if 'api_key' not in config or not config['api_key']:
                print(f"❌ Error: Missing API key for {model}")
                print(f"Please provide a valid API key in your configuration")
                print("You can set it via:")
                print("1. The 'api_key' field in your config dictionary")
                print("2. The appropriate environment variable:")
                print("   - OPENAI_API_KEY for OpenAI models")
                print("   - DEEPSEEK_API_KEY for DeepSeek models")
                print("   - GEMINI_API_KEY for Gemini models")
                print("   - GROQ_API_KEY for Groq models")
                exit(1)

            # Basic API key format validation
            api_key = config['api_key']
            if len(api_key) < 20 or not api_key.startswith(('sk-', 'ds-', 'AI')):
                print(f"❌ Error: Invalid API key format for {model}")
                print("API keys should be at least 20 characters long and start with:")
                print("- 'sk-' for OpenAI")
                print("- 'ds-' for DeepSeek")
                print("- 'AI' for Gemini")
                print("- 'ollama-' for Ollama (not required for localhost)") # <-- Added note about Ollama API key
                exit(1)

        # Register custom model clients
        register_deepseek_client()

        # Validate and create prompt configuration if provided
        prompt = None
        if prompt_config:
            try:
                prompt = PromptConfig.from_dict(prompt_config)
                errors = prompt.validate()
                if errors:
                    raise ValueError(f"Invalid prompt configuration: {', '.join(errors)}")
            except Exception as e:
                raise ValueError(f"Failed to create prompt configuration: {str(e)}")

        # Create appropriate implementation based on model
        model = config['model'].lower()

        # Existing Mistral-Nemo implementation
        if model == 'mistral-nemo-instruct-2407':
            return MistralNemoImplementation(
                base_url=config.get('base_url', 'http://localhost:1234/v1'),
                api_key=config.get('api_key', 'not-needed')
            )

        # LiteLLM-based implementations
        if model.startswith('openai/'):
            if 'api_key' not in config:
                raise ValueError("OpenAI implementation requires api_key")
            return OpenAIImplementation(
                model=model[7:],  # Remove 'openai/' prefix
                api_key=config['api_key']
            )

        if model.startswith('deepseek/') or model == 'deepseek-chat':
            if 'api_key' not in config:
                raise ValueError("DeepSeek implementation requires api_key")

            # Get model from environment
            model = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
            print(f"Python sees LLM_MODEL as: {os.getenv('LLM_MODEL')}")
            api_key = os.getenv('DEEPSEEK_API_KEY')

            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable not set")

            print(f"Using DeepSeek API with key length: {len(api_key)}")

            # Create config for agent
            config_list = [{
                "model": model,
                "api_key": api_key,
                "temperature": 0.7,
                "max_tokens": 4096
            }]

            # Create agents
            assistant = autogen.AssistantAgent(
                name="assistant",
                llm_config={"config_list": config_list},
                system_message="You are a helpful AI assistant."
            )

            user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=10,
                llm_config={"config_list": config_list}
            )

            # Register DeepSeek client with both agents
            register_deepseek_client(assistant)
            register_deepseek_client(user_proxy)

            # Create LiteLLM implementation with agents
            return DeepSeekImplementation(assistant=assistant, user_proxy=user_proxy)

        if model.startswith('gemini/'):
            if 'api_key' not in config:
                raise ValueError("Gemini implementation requires api_key")
            return GeminiImplementation(
                model=model[7:],  # Remove 'gemini/' prefix
                api_key=config['api_key']
            )

        if model.startswith('groq/'):
            if 'api_key' not in config:
                raise ValueError("Groq implementation requires api_key")
            return GroqImplementation(
                model=model[5:],  # Remove 'groq/' prefix
                api_key=config['api_key']
            )
        if model.startswith('ollama/'): # <-- Ollama implementation
            ollama_base_url = config.get('ollama_base_url')
            return OllamaImplementation(
                model=model[7:],  # Remove 'ollama/' prefix
                ollama_base_url=ollama_base_url # Pass base URL from config
            )


    @staticmethod
    def test_connection() -> bool:
        """Test connection to LLM services

        Returns:
            bool: True if connection test succeeds, False otherwise
        """
        try:
            # Get API key from environment
            api_key = os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                print("DEEPSEEK_API_KEY environment variable not set")
                return False

            # Test with DeepSeek configuration
            test_config = {
                'model': 'deepseek-chat',
                'api_key': api_key
            }

            # Create instance
            llm = LLMFactory.create_llm(test_config)

            if isinstance(llm, DeepSeekImplementation):
                print(f"Testing DeepSeek API connection with URL: {llm.client.api_base}, model: {llm.model_name}, key length: {len(llm.client.api_key)}")
                # Attempt a simple API call (e.g., get models) - this might need adjustment based on the DeepSeek API
                try:
                    llm.client.list_models()
                    return True
                except Exception as e:
                    print(f"DeepSeek API test failed: {e}")
                    return False
            else:
                print("Not a DeepSeek implementation, skipping direct API test.")
                return True  # Assume connection is okay for other types

        except Exception as e:
            # Connection failed
            print(f"Connection test failed: {str(e)}")
            return False