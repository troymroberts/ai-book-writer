from typing import Optional, Dict, Any, List
import os
from .litellm_base import LiteLLMBase
import litellm  # Ensure litellm is imported at the top
from .deepseek_client import DeepSeekClient
from types import SimpleNamespace
import autogen

class OpenAIImplementation(LiteLLMBase):
    """Implementation for OpenAI models"""

    def __init__(self, model: str, api_key: str, organization: Optional[str] = None, **kwargs):
        super().__init__(
            model=f"openai/{model}",
            api_key=api_key,
            organization=organization,
            **kwargs
        )

class DeepSeekImplementation(LiteLLMBase):
    """Implementation for DeepSeek models"""

    def __init__(self, config: Dict, **kwargs):
        """Initialize with configuration"""
        super().__init__(
            model="deepseek-chat",
            api_key=config.get("api_key"),
            base_url=config.get("base_url", "https://api.deepseek.com"),
            **kwargs
        )
        self.client = DeepSeekClient(config)

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using DeepSeek model"""
        response = self.client.generate(
            prompt=prompt,
            **kwargs
        )
        return response

    def generate_chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using DeepSeek model"""
        response = self.client.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response

class GeminiImplementation(LiteLLMBase):
    """Implementation for Google Gemini models"""

    def __init__(self, model: str, api_key: str, organization: Optional[str] = None, **kwargs):
        super().__init__(
            model=f"gemini/{model}",
            api_key=api_key,
            organization=organization,
            **kwargs
        )

class GroqImplementation(LiteLLMBase):
    """Implementation for Groq models"""

    def __init__(self, model: str, api_key: str, organization: Optional[str] = None, **kwargs):
        super().__init__(
            model=f"groq/{model}",
            api_key=api_key,
            organization=organization,
            **kwargs
        )

class OllamaImplementation(LiteLLMBase):
    """Implementation for Ollama models"""

    @classmethod
    def register_model(cls, model_name: str): # Pass in model_name to register for
        """Register this client class with autogen's configuration system"""
        autogen.oai.ChatCompletion.register_model( # Use autogen.oai, not just oai
            model_name, # Register for the specific model name (e.g., "ollama/llama2")
            cls,
            is_chat_model=True
        )

    def __init__(self, model: str, api_key: str = None, ollama_base_url: str = None, **kwargs):
        super().__init__(
            model=f"ollama/{model}", # Keep full ollama model string for internal model tracking
            base_url=ollama_base_url or os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            api_key=api_key,  # Ollama typically doesn't need an API key for local deployment
            **kwargs
        )

    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama model"""
        response = self.generate(prompt, **kwargs)
        return response

    def generate_chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using Ollama model"""
        return super().generate(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    def create(self, params: Dict) -> SimpleNamespace: # Modified create method
        """Adapt generate to return SimpleNamespace for autogen"""
        # model_name_for_litellm = self.model.split('/')[-1].split(':')[0] # No longer needed - use full model string
        response = litellm.completion( # Call litellm.completion directly, passing FULL model string
            model=self.model, # Use FULL model string, e.g., "ollama/deepseek-r1:14b" # Modified line - use full model string NOW
            messages=params["messages"],
            base_url=self.base_url,
            provider="ollama" # Explicitly set the provider to ollama
        )
        response_content = response.choices[0].message.content
        result = SimpleNamespace()
        result.choices = [SimpleNamespace(message=SimpleNamespace(content=response_content, role="assistant", function_call=None))]
        result.model = self.model # Keep full ollama model string for internal tracking
        return result


class O1PreviewImplementation(LiteLLMBase):
    """Implementation for O1-Preview models"""

    def __init__(self, model: str, api_key: str, organization: Optional[str] = None, **kwargs):
        super().__init__(
            model=f"o1/{model}",
            api_key=api_key,
            base_url="https://api.o1.ai/v1",
            **kwargs
        )

class GeminiFlashImplementation(LiteLLMBase):
    """Implementation for Gemini 2.0 Flash Experimental models"""

    def __init__(self, model: str, api_key: str, organization: Optional[str] = None, **kwargs):
        super().__init__(
            model=f"gemini-flash/{model}",
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta",
            **kwargs
        )