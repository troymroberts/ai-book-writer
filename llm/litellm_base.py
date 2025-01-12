from typing import Generator, Optional, List, Dict, Any
import os
import logging
import litellm
import httpx
from .interface import LLMInterface

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiteLLMBase(LLMInterface):
    """Base class for LiteLLM-based implementations with enhanced features
    
    Features:
    - Environment variable based configuration
    - Advanced error handling with retries
    - Modular model management
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        logger.info(f"Initializing LiteLLMBase with model: {model}")
        self.model = model
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.base_url = base_url or os.getenv('OPENAI_BASE_URL')
        self.organization = organization or os.getenv('OPENAI_ORG_ID')
        self.total_tokens = 0
        self.response_headers = {}
        self.retry_count = int(os.getenv('LITELLM_RETRY_COUNT', '3'))
        self.retry_delay = float(os.getenv('LITELLM_RETRY_DELAY', '1.0'))
        
        if not self.api_key:
            error_msg = "API key must be provided or set in environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        logger.info("LiteLLMBase initialization complete")
        
    def generate(
        self,
        prompt: str,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = None
    ) -> str:
        """Generate text from a prompt with optional function calling"""
        import time
        from litellm.exceptions import (
            RateLimitError,
            ServiceUnavailableError,
            APIError
        )
        
        logger.info(f"Generating response for prompt (length: {len(prompt)})")
        if functions:
            logger.debug(f"Using functions: {[f['name'] for f in functions]}")
        
        # Only include standard LiteLLM parameters
        params = {
            "model": self.model,
            "messages": [{"content": prompt, "role": "user"}],
            "api_key": self.api_key,
        }
        
        # Optionally add non-null parameters
        if self.base_url:
            params["base_url"] = self.base_url
        if self.organization:
            params["organization"] = self.organization
        
        if functions:
            params["functions"] = functions
            params["function_call"] = function_call or "auto"
        
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = litellm.completion(
                    return_response_headers=True,
                    **params
                )
                
                # Update usage and store headers
                self.total_tokens += response.usage.total_tokens
                self.response_headers = response._headers
                
                return response.choices[0].message.content
                
            except RateLimitError as e:
                last_error = e
                time.sleep(self.retry_delay * (attempt + 1))
            except ServiceUnavailableError as e:
                last_error = e
                time.sleep(self.retry_delay * (attempt + 1))
            except APIError as e:
                last_error = e
                if e.status_code == 429:  # Rate limit
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except Exception as e:
                last_error = e
                raise
        
        raise RuntimeError(
            f"Failed after {self.retry_count} attempts. Last error: {str(last_error)}"
        )
    
    def stream(
        self,
        prompt: str,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[str] = None
    ) -> Generator[str, None, None]:
        """Stream text generation from a prompt with optional function calling"""
        import time
        from litellm.exceptions import (
            RateLimitError,
            ServiceUnavailableError,
            APIError
        )
        
        logger.info(f"Starting stream for prompt (length: {len(prompt)})")
        if functions:
            logger.debug(f"Using functions: {[f['name'] for f in functions]}")
        
        # Only include standard LiteLLM parameters
        params = {
            "model": self.model,
            "messages": [{"content": prompt, "role": "user"}],
            "api_key": self.api_key,
            "stream": True,
        }
        
        # Optionally add non-null parameters
        if self.base_url:
            params["base_url"] = self.base_url
        if self.organization:
            params["organization"] = self.organization
        
        if functions:
            params["functions"] = functions
            params["function_call"] = function_call or "auto"
        
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = litellm.completion(
                    **params
                )
                
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        self.total_tokens += 1
                        yield chunk.choices[0].delta.content
                return
                
            except RateLimitError as e:
                last_error = e
                time.sleep(self.retry_delay * (attempt + 1))
            except ServiceUnavailableError as e:
                last_error = e
                time.sleep(self.retry_delay * (attempt + 1))
            except APIError as e:
                last_error = e
                if e.status_code == 429:  # Rate limit
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except Exception as e:
                last_error = e
                raise
        
        raise RuntimeError(
            f"Failed after {self.retry_count} attempts. Last error: {str(last_error)}"
        )
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics for the LLM"""
        return {
            "total_tokens": self.total_tokens,
            "model": self.model,
            "response_headers": self.response_headers
        }

    def test_connection(self) -> bool:
        """Test connection to the LLM service with advanced options"""
        import time
        from litellm.exceptions import (
            RateLimitError,
            ServiceUnavailableError,
            APIError
        )
        
        logger.info("Testing connection to LLM service")
        
        # Only include standard LiteLLM parameters
        params = {
            "model": self.model,
            "messages": [{"content": "test", "role": "user"}],
            "api_key": self.api_key,
            "max_tokens": 1,
        }
        
        # Optionally add non-null parameters
        if self.base_url:
            params["base_url"] = self.base_url
        if self.organization:
            params["organization"] = self.organization
        
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = litellm.completion(
                    **params
                )
                logger.info("Connection test successful")
                return True
            except RateLimitError as e:
                last_error = e
                logger.warning(f"Rate limited, retrying in {self.retry_delay * (attempt + 1)}s")
                time.sleep(self.retry_delay * (attempt + 1))
            except ServiceUnavailableError as e:
                last_error = e
                logger.warning(f"Service unavailable, retrying in {self.retry_delay * (attempt + 1)}s")
                time.sleep(self.retry_delay * (attempt + 1))
            except APIError as e:
                last_error = e
                if e.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limited, retrying in {self.retry_delay * (attempt + 1)}s")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"API error: {str(e)}")
                    break
            except Exception as e:
                last_error = e
                logger.error(f"Connection test failed: {str(e)}")
                break
        
        logger.error(f"Failed to connect after {self.retry_count} attempts")
        return False

    def parallel_function_call(
        self,
        prompt: str,
        functions: List[Dict[str, Any]],
        function_call: str = "auto"
    ) -> List[Dict[str, Any]]:
        """Perform parallel function calling with error handling"""
        import time
        from litellm.exceptions import (
            RateLimitError,
            ServiceUnavailableError,
            APIError
        )
        
        logger.info(f"Starting parallel function call with {len(functions)} functions")
        logger.debug(f"Functions: {[f['name'] for f in functions]}")
        
        # Only include standard LiteLLM parameters
        params = {
            "model": self.model,
            "messages": [{"content": prompt, "role": "user"}],
            "api_key": self.api_key,
            "functions": functions,
            "function_call": function_call,
        }
        
        # Optionally add non-null parameters
        if self.base_url:
            params["base_url"] = self.base_url
        if self.organization:
            params["organization"] = self.organization
        
        last_error = None
        for attempt in range(self.retry_count):
            try:
                response = litellm.completion(
                    **params
                )
                
                # Update usage
                self.total_tokens += response.usage.total_tokens
                
                # Process and return function call results
                results = [
                    {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                    for call in response.choices[0].message.tool_calls
                ]
                
                logger.info(f"Successfully processed {len(results)} function calls")
                return results
                
            except RateLimitError as e:
                last_error = e
                logger.warning(f"Rate limited, retrying in {self.retry_delay * (attempt + 1)}s")
                time.sleep(self.retry_delay * (attempt + 1))
            except ServiceUnavailableError as e:
                last_error = e
                logger.warning(f"Service unavailable, retrying in {self.retry_delay * (attempt + 1)}s")
                time.sleep(self.retry_delay * (attempt + 1))
            except APIError as e:
                last_error = e
                if e.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limited, retrying in {self.retry_delay * (attempt + 1)}s")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"API error: {str(e)}")
                    break
            except Exception as e:
                last_error = e
                logger.error(f"Function call failed: {str(e)}")
                break
        
        raise RuntimeError(
            f"Failed after {self.retry_count} attempts. Last error: {str(last_error)}"
        )
