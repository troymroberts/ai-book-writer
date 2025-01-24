"""Define the agents used in the book generation system with improved context management and specialized roles"""
import autogen
from typing import Dict, List, Optional
from llm.factory import LLMFactory
from llm.deepseek_client import DeepSeekClient # <-- Keep this import for DeepSeek-specific client (if needed later)
from llm.litellm_implementations import OllamaImplementation # <-- Import OllamaImplementation
from config import get_config

class BookAgents:
    def __init__(self, agent_config: Dict, outline: Optional[List[Dict]] = None, genre_config: Optional[Dict] = None):
        """Initialize agents with book outline context and genre configuration"""
        self.agent_config = self._prepare_autogen_config(agent_config)
        self.outline = outline
        self.genre_config = genre_config or {}
        self.world_elements = {}  # Track described locations/elements
        self.character_developments = {}  # Track character arcs

    def _prepare_autogen_config(self, config: Dict) -> Dict:
        """Prepare configuration for autogen compatibility"""
        # Convert config to dict if it's a Pydantic model
        if hasattr(config, 'dict'):
            config = config.dict()
        llm_config = get_config()

        config_list = [] # Initialize as empty list

        model_lower = llm_config.get("model", "").lower() # Get model and lowercase it

        if "ollama" in model_lower: # Check if Ollama model is selected
            config_list.append({
                "model": llm_config.get("model"), # Use model from config (e.g., ollama/deepseek-r1:14b)
                "base_url": llm_config.get("base_url"), # Use base_url from config
                "api_key": llm_config.get("api_key"), # Pass API key even if it's None/empty for Ollama (LiteLLM might need it, though Ollama usually doesn't)
                "model_client_cls": "OllamaImplementation", # Use Ollama implementation
                "model_kwargs": {}
            })
        else: # Default to DeepSeek if not Ollama (or handle other models here in future)
            config_list.append({
                "model": "deepseek-chat", # Default to deepseek-chat if not Ollama
                "api_key": llm_config.get("api_key"),
                "base_url": llm_config.get("base_url"),
                "model_client_cls": "DeepSeekClient",
                "model_kwargs": {}
            })


        return {
            **config,
            "config_list": config_list,
            # Remove hardcoded DeepSeekClient - client will be dynamically chosen based on config
            # "model_client_cls": DeepSeekClient  <- REMOVE THIS LINE
        }

    # ... (rest of _get_genre_style_instructions, _format_outline_context, _prepare_chapter_context - unchanged) ...

    def create_agents(self, initial_prompt, num_chapters) -> Dict:
        """Create and return all agents needed for book generation with specialized roles"""
        outline_context = self._format_outline_context()

        # ... (Memory Keeper, Story Planner, Outline Creator, Setting Builder, Character Agent, Plot Agent, Writer, Editor, User Proxy - agent definitions - unchanged) ...

        agent_list = [memory_keeper, story_planner, outline_creator, setting_builder, character_agent, plot_agent, writer, editor, user_proxy] # List of agents

        llm_config = get_config() # Get config again to access model info

        model_lower = llm_config.get("model", "").lower() # Get model name again

        # Dynamically register model client based on LLM_MODEL
        if "ollama" in model_lower:
            model_client_cls = OllamaImplementation # Use Ollama client for Ollama models
        else:
            model_client_cls = DeepSeekClient # Default to DeepSeek for other models (or adjust as needed)

        for agent in agent_list:
            agent.register_model_client(model_client_cls=model_client_cls) # Register dynamically

        return {
            "story_planner": story_planner,
            "setting_builder": setting_builder, # Renamed and using setting_builder now
            "character_agent": character_agent, # Added character_agent
            "plot_agent": plot_agent, # Added plot_agent
            "memory_keeper": memory_keeper,
            "writer": writer,
            "editor": editor,
            "user_proxy": user_proxy,
            "outline_creator": outline_creator
        }

    # ... (rest of update_world_element, update_character_development, get_world_context, get_character_context - unchanged) ...