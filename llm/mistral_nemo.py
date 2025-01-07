from typing import Generator
import requests
from .interface import LLMInterface

class MistralNemoImplementation(LLMInterface):
    """Implementation for Mistral-Nemo-Instruct LLM"""
    
    def __init__(self, base_url: str, api_key: str = "not-needed"):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.usage_stats = {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0
        }

    def generate(self, prompt: str) -> str:
        """Generate text from a prompt"""
        try:
            response = self.session.post(
                f"{self.base_url}/completions",
                json={
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            result = response.json()
            
            # Update usage statistics
            self._update_usage(result.get('usage', {}))
            
            return result['choices'][0]['text']
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    def stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream text generation from a prompt"""
        try:
            with self.session.post(
                f"{self.base_url}/completions",
                json={
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": True
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                stream=True
            ) as response:
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
        except Exception as e:
            raise RuntimeError(f"LLM streaming failed: {str(e)}")

    def get_usage(self) -> dict:
        """Get usage statistics for the LLM"""
        return self.usage_stats.copy()

    def test_connection(self) -> bool:
        """Test connection to the Mistral-Nemo service"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5  # Add timeout to prevent hanging
            )
            # Return True only for 200 status code
            return response.status_code == 200
        except Exception:
            # Return False for any connection error or timeout
            return False

    def _update_usage(self, usage: dict):
        """Update internal usage statistics"""
        self.usage_stats['total_tokens'] += usage.get('total_tokens', 0)
        self.usage_stats['prompt_tokens'] += usage.get('prompt_tokens', 0)
        self.usage_stats['completion_tokens'] += usage.get('completion_tokens', 0)

    def generate_with_template(self, template: str, values: dict) -> str:
        """Generate text using a template with placeholders"""
        try:
            # Validate template format
            from string import Formatter
            formatter = Formatter()
            formatter.parse(template)
            
            # Format the template with provided values
            formatted_prompt = template.format(**values)
            return self.generate(formatted_prompt)
        except ValueError as e:
            raise ValueError(f"Invalid template format: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Missing template value for: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Template generation failed: {str(e)}")

    def stream_with_template(self, template: str, values: dict) -> Generator[str, None, None]:
        """Stream text generation using a template with placeholders"""
        try:
            # Validate template format
            from string import Formatter
            formatter = Formatter()
            formatter.parse(template)
            
            # Format the template with provided values
            formatted_prompt = template.format(**values)
            
            # Process each chunk from the stream
            with self.session.post(
                f"{self.base_url}/completions",
                json={
                    "prompt": formatted_prompt,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": True
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                stream=True
            ) as response:
                response.raise_for_status()
                
                for chunk in response.iter_content(chunk_size=None):
                    if chunk:
                        yield chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk
        except ValueError as e:
            raise ValueError(f"Invalid template format: {str(e)}")
        except KeyError as e:
            raise ValueError(f"Missing template value for: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Template streaming failed: {str(e)}")
