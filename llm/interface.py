from abc import ABC, abstractmethod
from typing import Generator, Optional, Union
from .prompt import PromptConfig

class LLMInterface(ABC):
    """Abstract base class for LLM implementations"""
    
    @abstractmethod
    def generate(self, prompt: Union[str, PromptConfig]) -> str:
        """
        Generate text from a prompt or template
        
        Args:
            prompt: Either a string prompt or PromptConfig instance
            
        Returns:
            Generated text output
        """
        pass
    
    @abstractmethod
    def stream(self, prompt: Union[str, PromptConfig]) -> Generator[str, None, None]:
        """
        Stream text generation from a prompt or template
        
        Args:
            prompt: Either a string prompt or PromptConfig instance
            
        Yields:
            Chunks of generated text
        """
        pass
    
    @abstractmethod
    def get_usage(self) -> dict:
        """Get usage statistics for the LLM"""
        pass
    
    def generate_with_template(self, template: str, variables: Optional[dict] = None) -> str:
        """
        Generate text using a template with variables
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of template variables
            
        Returns:
            Generated text output
        """
        prompt_config = PromptConfig(template, variables)
        return self.generate(prompt_config)
    
    def stream_with_template(self, template: str, variables: Optional[dict] = None) -> Generator[str, None, None]:
        """
        Stream text generation using a template with variables
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of template variables
            
        Yields:
            Chunks of generated text
        """
        prompt_config = PromptConfig(template, variables)
        yield from self.stream(prompt_config)

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connection to the LLM service
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass
