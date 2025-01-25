# ollama_autogen_test.py - WITH REGISTER_MODEL() CALL
import autogen
import logging

# Enable DEBUG logging for this test script
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from llm.litellm_implementations import OllamaImplementation

# REGISTER OLLAMA IMPLEMENTATION EXPLICITLY - ADDED THIS LINE
OllamaImplementation.register_model(model_name="ollama/deepseek-r1:14b") # Register for the specific model

# Configuration for Ollama agent - using model_client_cls (unchanged)
ollama_config = {
    "model": "ollama/deepseek-r1:14b",  # Or your Ollama model - MATCH REGISTRATION NAME
    "base_url": "http://localhost:11434", # Your Ollama base URL
    "api_key": None, # No API key needed for local Ollama
    "model_client_cls": OllamaImplementation, # Explicitly set model_client_cls
    "model_kwargs": {},
}

config_list_ollama = [ollama_config]

# Create UserProxyAgent (unchanged)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config=False,
)

# Create AssistantAgent configured for Ollama - IMPORTANT: pass config_list directly in llm_config (unchanged)
assistant = autogen.AssistantAgent(
    name="assistant_ollama",
    llm_config={
        "config_list": config_list_ollama, # Pass config_list here
        "model": "ollama/deepseek-r1:14b", # Redundant but explicit - model name also here - MATCH REGISTRATION NAME
    },
    system_message="You are a helpful AI assistant. You are using Ollama via LiteLLM."
)

logger.debug("UserProxyAgent created")
logger.debug("AssistantAgent (Ollama) created")
logger.debug(f"Assistant Agent llm_config: {assistant.llm_config}")

# Start a simple chat (unchanged)
user_proxy.initiate_chat(
    assistant,
    message="Write a very short test sentence using Ollama.",
)

logger.debug("Chat initiated")