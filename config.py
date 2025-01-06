"""Configuration for the book generation system"""
import os
from typing import Dict, List, Optional, Union
from llm.factory import LLMFactory
from llm.prompt import PromptConfig

def create_llm(config: Dict, prompt_config: Optional[Dict] = None) -> LLMInterface:
    """Create an LLM instance from configuration
    
    Args:
        config: LLM configuration dictionary
        prompt_config: Optional prompt template configuration
        
    Returns:
        Configured LLMInterface instance
    """
    return LLMFactory.create_llm(config, prompt_config)

def get_llm_config(
    model: str, 
    api_key: Optional[str] = None,
    prompt_template: Optional[str] = None,
    prompt_variables: Optional[Dict[str, str]] = None
) -> Dict:
    """Get configuration for a specific LLM model"""
    config = {'model': model}
    
    # Set API key from environment variable if not provided
    if api_key is None:
        if model.startswith('openai/'):
            api_key = os.getenv('OPENAI_API_KEY')
        elif model.startswith('deepseek/'):
            api_key = os.getenv('DEEPSEEK_API_KEY')
        elif model.startswith('gemini/'):
            api_key = os.getenv('GEMINI_API_KEY')
        elif model.startswith('groq/'):
            api_key = os.getenv('GROQ_API_KEY')
    
    if api_key:
        config['api_key'] = api_key
        
    # Local model configuration
    if model == 'mistral-nemo-instruct-2407':
        config['base_url'] = os.getenv('LOCAL_LLM_URL', 'http://localhost:1234/v1')
    
    return config

def get_config(local_url: str = "http://localhost:1234/v1") -> Dict:
    """Get the configuration for the agents"""
    
    # Get model from environment or use default
    model = os.getenv('LLM_MODEL', 'mistral-nemo-instruct-2407')
    
    # Create config list with primary model
    config_list = [get_llm_config(model)]
    
    # Add fallback models if specified
    fallback_models = os.getenv('LLM_FALLBACK_MODELS', '').split(',')
    for fallback in fallback_models:
        if fallback.strip():
            config_list.append(get_llm_config(fallback.strip()))

    # Common configuration for all agents
    agent_config = {
        "seed": 42,
        "temperature": 0.7,
        "config_list": config_list,
        "timeout": 600,
        "cache_seed": None
    }
    
    return agent_config
