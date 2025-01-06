from typing import Generator, Optional
from litellm import completion
from .interface import LLMInterface

class LiteLLMBase(LLMInterface):
    """Base class for LiteLLM-based implementations"""
    
    def __init__(self, model: str, api_key: Optional[str] = None, base_url: Optional[str] = None, **kwargs):
        self.model = model
        self.api_key = api_key
        self.base_url = kwargs.get('api_base', base_url)
        self.total_tokens = 0
        
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt"""
        response = completion(
            model=self.model,
            messages=[{"content": prompt, "role": "user"}],
            api_key=self.api_key,
            base_url=self.base_url,
        )
        self.total_tokens += response.usage.total_tokens
        return response.choices[0].message.content
    
    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream text generation from a prompt"""
        response = completion(
            model=self.model,
            messages=[{"content": prompt, "role": "user"}],
            api_key=self.api_key,
            base_url=self.base_url,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                self.total_tokens += 1
                yield chunk.choices[0].delta.content
    
    def get_usage(self) -> dict:
        """Get usage statistics for the LLM"""
        return {
            "total_tokens": self.total_tokens,
            "model": self.model
        }

    def test_connection(self) -> bool:
        """Test connection to the LLM service"""
        try:
            # Attempt a simple API call
            response = completion(
                model=self.model,
                messages=[{"content": "test", "role": "user"}],
                api_key=self.api_key,
                base_url=self.base_url,
                max_tokens=1
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False
