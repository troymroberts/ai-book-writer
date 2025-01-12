"""Custom model client for DeepSeek API following AutoGen protocol"""
from types import SimpleNamespace
from typing import Dict, List, Optional, Union
import requests
import os
import logging
import time
from autogen import oai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekClient:
    """Custom client for DeepSeek API following autogen ModelClient protocol"""
    
    @classmethod
    def register_model(cls, model_name: str = "deepseek-chat"):
        """Register this client class with autogen's configuration system"""
        oai.ChatCompletion.register_model(
            model_name,
            cls,
            is_chat_model=True
        )
    
    def __init__(self, config: Dict, **kwargs):
        """Initialize DeepSeek client with configuration"""
        # Convert SecretStr values to plain strings in config
        self.config = {
            k: v.get_secret_value() if hasattr(v, 'get_secret_value') else v
            for k, v in config.items()
        }
        
        # Handle API key
        self.api_key = self.config.get('api_key')
        if not self.api_key:
            raise ValueError("API key not provided in config")
            
        self.base_url = config.get('base_url', 'https://api.deepseek.com')
        self.chat_endpoint = f"{self.base_url}/chat/completions"
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 4096)
        self.retry_count = int(os.getenv('LITELLM_RETRY_COUNT', '3'))
        self.retry_delay = float(os.getenv('LITELLM_RETRY_DELAY', '1.0'))
        
        logger.info("DeepSeek client initialized with API key length: %d", len(self.api_key))
        logger.info("Using base URL: %s", self.base_url)
        
    def test_connection(self) -> bool:
        """Test the API connection"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error("Connection test failed: %s", str(e))
            return False
        
    def create(self, params: Dict) -> SimpleNamespace:
        """Create a chat completion using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Log request details (excluding API key)
        logger.info("Making request to: %s", self.chat_endpoint)
        logger.info("Headers (excluding auth): %s", {k:v for k,v in headers.items() if k != 'Authorization'})
        
        # Prepare the request payload
        payload = {
            "model": self.config.get('model', 'deepseek-chat'),
            "messages": params.get("messages", []),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False
        }
        
        logger.info("Request payload: %s", payload)
        
        last_error = None
        for attempt in range(self.retry_count):
            try:
                # Make the API request
                logger.info("Attempt %d/%d", attempt + 1, self.retry_count)
                response = requests.post(
                    self.chat_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                
                # Log response details
                logger.info("Response status: %d", response.status_code)
                logger.info("Response headers: %s", response.headers)
                logger.info("Response body: %s", response.text)
                
                response.raise_for_status()
                data = response.json()
                
                # Convert to SimpleNamespace to match protocol
                result = SimpleNamespace()
                result.choices = []
                result.model = "deepseek-chat"
                
                # Extract the message from the response
                if data.get('choices') and len(data['choices']) > 0:
                    for choice in data['choices']:
                        choice_obj = SimpleNamespace()
                        choice_obj.message = SimpleNamespace()
                        choice_obj.message.content = choice['message']['content']
                        choice_obj.message.role = choice['message']['role']
                        choice_obj.message.function_call = None
                        result.choices.append(choice_obj)
                
                logger.info("Successfully processed response")
                return result
                
            except Exception as e:
                last_error = e
                logger.error("Error in attempt %d: %s", attempt + 1, str(e))
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                logger.error("Failed after %d attempts", self.retry_count)
                raise last_error

    def message_retrieval(self, response: SimpleNamespace) -> List[str]:
        """Retrieve messages from the response"""
        return [choice.message.content for choice in response.choices]

    def cost(self, response: SimpleNamespace) -> float:
        """Calculate cost of the response (placeholder)"""
        return 0.0

    @staticmethod
    def get_usage(response: SimpleNamespace) -> Dict:
        """Return usage statistics (placeholder)"""
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost": 0,
            "model": "deepseek-chat"
        }
        
    def can_handle_message(self, message: Dict) -> bool:
        """Check if this client can handle the given message"""
        return True  # This client can handle all messages
