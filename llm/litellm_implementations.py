from typing import Optional
from .litellm_base import LiteLLMBase

class OpenAIImplementation(LiteLLMBase):
    """Implementation for OpenAI models"""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model=f"openai/{model}", api_key=api_key)

class DeepSeekImplementation(LiteLLMBase):
    """Implementation for DeepSeek models"""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model=f"deepseek/{model}", api_key=api_key)

class GeminiImplementation(LiteLLMBase):
    """Implementation for Google Gemini models"""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model=f"gemini/{model}", api_key=api_key)

class GroqImplementation(LiteLLMBase):
    """Implementation for Groq models"""
    
    def __init__(self, model: str, api_key: str):
        super().__init__(model=f"groq/{model}", api_key=api_key)
