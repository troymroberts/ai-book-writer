import os
from typing import Dict, Optional
from .mistral_nemo import MistralNemoImplementation
from .litellm_implementations import (
    OpenAIImplementation,
    DeepSeekImplementation,
    GeminiImplementation,
    GroqImplementation
)
from .interface import LLMInterface
from .prompt import PromptConfig

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
            raise ValueError("LLM config must be a dictionary")
            
        if 'model' not in config:
            raise ValueError("LLM config must specify a model")
            
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
            
        if model.startswith('deepseek/'):
            if 'api_key' not in config:
                raise ValueError("DeepSeek implementation requires api_key")
            return DeepSeekImplementation(
                model=model[9:],  # Remove 'deepseek/' prefix
                api_key=config['api_key']
            )
            
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
            
    @staticmethod
    def test_connection() -> bool:
        """Test connection to LLM services
        
        Returns:
            bool: True if connection test succeeds, False otherwise
        """
        try:
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("OPENAI_API_KEY environment variable not set")
                return False
                
            # Test with a simple OpenAI model configuration
            test_config = {
                'model': 'openai/gpt-3.5-turbo',
                'api_key': api_key
            }
            
            # Create instance and attempt connection
            llm = LLMFactory.create_llm(test_config)
            
            # Try to make a simple API call
            result = llm.test_connection()
            return result
            
        except Exception as e:
            # Connection failed
            print(f"Connection test failed: {str(e)}")
            return False
