# smolagents_ollama_test.py - CORRECTED INSTALL INSTRUCTION (pip install smolagents) - SCRIPT CODE UNCHANGED
from smolagents.agents.functional_agent import FunctionalAgent  # Correct import - smolagents (no hyphen)
from smolagents.llms.litellm import LiteLLMConfig, LiteLLM_LLM # Correct import - smolagents (no hyphen)
import logging

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("--- Smolagents Ollama Test Script Started ---")

# Define LiteLLMConfig for Ollama
ollama_config = LiteLLMConfig(
    model="ollama/deepseek-r1:14b",  # Or your Ollama model
    base_url="http://localhost:11434", # Your Ollama base URL
    api_key=None, # No API key needed for local Ollama
    provider="ollama" # Explicitly set the provider to ollama for LiteLLM
)

logger.debug("LiteLLMConfig for Ollama created:")
logger.debug(f"Model: {ollama_config.model}")
logger.debug(f"Base URL: {ollama_config.base_url}")
logger.debug(f"Provider: {ollama_config.provider}")

# Create LiteLLM_LLM instance using the config
ollama_llm = LiteLLM_LLM(ollama_config)

logger.debug("LiteLLM_LLM instance created")
logger.debug(f"LLM Model Name: {ollama_llm.model_name}")
logger.debug(f"LLM Base URL: {ollama_llm.base_url}")
logger.debug(f"LLM Provider: {ollama_llm.provider_name}")


# Create a FunctionalAgent - simplest agent in Smolagents
agent = FunctionalAgent(
    llm=ollama_llm, # Pass the LiteLLM_LLM instance
    name="ollama_test_agent",
    system_message="You are a simple AI agent using Ollama for text generation."
)

logger.debug("FunctionalAgent created")
logger.debug(f"Agent Name: {agent.name}")
logger.debug(f"Agent LLM: {agent.llm.model_name} (Provider: {agent.llm.provider_name})")


# Define a simple task
test_prompt = "Write a very short test sentence using Ollama."
logger.debug(f"Test prompt: {test_prompt}")

# Run the agent and get response
try:
    response = agent.run(test_prompt)
    logger.debug("Agent run completed successfully")
    print("\n--- Smolagents Ollama Test Response ---")
    print(response)

except Exception as e:
    logger.error(f"Error during agent run: {e}")
    import traceback
    traceback.print_exc()

logger.debug("--- Smolagents Ollama Test Script Finished ---")