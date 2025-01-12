from typing import Optional, Dict, Any
import os
from .litellm_base import LiteLLMBase

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
    
    def __init__(self, assistant, user_proxy):
        """Initialize with autogen agents"""
        self.assistant = assistant
        self.user_proxy = user_proxy
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using DeepSeek model via autogen"""
        # Initialize chat between agents
        self.user_proxy.initiate_chat(
            self.assistant,
            message=prompt,
            clear_history=True
        )
        
        # Return the last message from the assistant
        return self.assistant.last_message()["content"]
        
    def generate_chat_completion(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate chat completion using DeepSeek model"""
        # Format the conversation for the assistant
        formatted_prompt = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        # Get response from assistant
        response = self.generate_text(formatted_prompt)
        
        # Format response in chat completion style
        return {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response
                }
            }]
        }

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
