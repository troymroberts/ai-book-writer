"""Module for registering custom model clients with autogen"""
import os
import logging
import autogen
from .deepseek_client import DeepSeekClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_deepseek_client(agent):
    """Register DeepSeek client with an autogen agent"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
    logger.info("Registering DeepSeek client with API key length: %d", len(api_key))
    
    # Create config for DeepSeek
    config = {
        "model": "deepseek-chat",
        "api_key": api_key,
        "temperature": 0.7,
        "max_tokens": 4096,
        "base_url": "https://api.deepseek.com/v1",
        "use_deepseek": True  # Flag to indicate this is a DeepSeek client
    }
    
    # Create the client instance
    client = DeepSeekClient(config=config)
    
    # Register the client with autogen
    agent._llm_config = {
        "config_list": [config],
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 4096
    }
    agent._model_client = client
    
    logger.info("Successfully registered DeepSeek client")
