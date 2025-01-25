"""Main script for running the book generation system - now with SIGTERM signal handling"""
#!/usr/bin/env python3
import autogen # <----- ADD THIS LINE:  Crucial import for AutoGen
print(f"--- DEBUG: AutoGen version at runtime: {autogen.__version__} ---") # ADD THIS LINE - Debug print for AutoGen version
print("--- main.py script started ---")
print("--- Debugging main.py: CUSTOM_OUTLINE check ---")
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("--- DEBUG: Main script started in DEBUG mode ---")  # Add this line

print("--- Standard output test from main.py ---") # Keep this print
from logging.config import dictConfig
import json
from config import get_settings
import signal
import sys

print(f"Python sys.path: {sys.path}")  # Print Python path for debugging

# Configure logging (simplified for brevity)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator
from fixed_outline import fixed_outline_data  # ADD THIS LINE - import fixed outline

stop_book_generation = False

def signal_handler(sig, frame):
    global stop_book_generation
    print("\nStopping book generation process...")
    stop_book_generation = True
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

def load_custom_outline(outline_path):
    chapters = []
    if os.path.exists(outline_path):
        with open(outline_path, 'r') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("Chapter"):
                    chapter_num = int(line.split(":")[0].split(" ")[1])
                    title = line.split(":")[1].strip()
                    i += 2  # Skip the separator line
                    prompt_lines = []
                    while i < len(lines) and not lines[i].strip().startswith("Chapter"):
                        prompt_line = lines[i].strip()
                        if prompt_line:
                            prompt_lines.append(prompt_line)
                        i += 1
                    prompt = "\n".join(prompt_lines)
                    chapters.append({
                        "chapter_number": chapter_num,
                        "title": title,
                        "prompt": prompt
                    })
                else:
                    i += 1
    else:
        print(f"Custom outline file not found at {outline_path}")
    return chapters

def load_genre_config(genre_name=None):
    # ... (rest of your load_genre_config function - unchanged) ...
    return {}

def apply_genre_config_to_agents(agents, genre_config):
    # ... (rest of your apply_genre_config_to_agents function - unchanged) ...
    return agents

def display_startup_info(genre_config, outline):
    """Display startup information and wait for user confirmation"""
    print("\n=== Book Generation Configuration ===")
    # ... (rest of your display_startup_info function - unchanged) ...
    input("\nPress Enter to start book generation...")

def main():
    print("--- main() function in main.py started ---")
    global stop_book_generation

    genre = os.getenv('BOOK_GENRE')
    print(f"--- BOOK_GENRE env var in main.py: {genre} ---")
    if not genre:
        print("No genre selected. Please run './select_genre.py' first.")
        return

    settings = get_settings()
    print("--- Settings object created in main.py ---")

    # ... (API key validation section - unchanged) ...

    genre_config = load_genre_config(genre)
    logger.debug(f"Loaded genre config: {genre_config}")

    initial_prompt = "Write a book about a dystopian future where AI controls society."  # Example prompt
    print(f"Initial prompt: {initial_prompt}")

    num_chapters = settings.generation.max_chapters
    # --- MOVED BookAgents and agents CREATION UP HERE, BEFORE the if/else block ---
    # Create agents with genre configuration (BookAgents now expects outline=None initially)
    outline_agents = BookAgents(settings.llm, None, genre_config)  # Pass outline=None initially
    print("--- BookAgents (outline) created in main.py ---")

    # --- DEBUGGING PRINTS - ADDED HERE ---
    print("--- DEBUG: LLM Config BEFORE agent creation ---")
    llm_config_for_agents = settings.get_llm_config() # Get LLM config dict
    print(f"--- DEBUG: llm_config from settings.get_llm_config(): {llm_config_for_agents}") # Print the config dict
    print(f"--- DEBUG: settings.llm: {settings.llm}") # Print the settings.llm object itself
    print("--- DEBUG: End LLM Config ---")
    # --- END DEBUGGING PRINTS ---

    agents = outline_agents.create_agents(initial_prompt, num_chapters)
    print("--- Agents created in main.py ---")
    # --- END MOVED SECTION ---

    # Check if using custom outline
    custom_outline_path = os.getenv('CUSTOM_OUTLINE')
    print(f"--- DEBUG: CUSTOM_OUTLINE env var value: '{custom_outline_path}' (Type: {type(custom_outline_path)}) ---")

    outline = None
    use_fixed_outline = os.getenv('USE_FIXED_OUTLINE', 'False').lower() == 'true'  # ADD THIS LINE - check for env var

    if use_fixed_outline:  # ADD THIS BLOCK - use fixed outline if env var is set
        print("--- DEBUG: Using FIXED OUTLINE from fixed_outline.py ---")
        outline = fixed_outline_data
    elif custom_outline_path and os.path.exists(custom_outline_path): # Changed to ELIF
        print("--- DEBUG: Custom outline path condition is TRUE ---")
        logger.info(f"Loading custom outline from: {custom_outline_path}")
        outline = load_custom_outline(custom_outline_path)
        if not outline:
            logger.error("Failed to load custom outline, check format")
            return
        logger.info(f"Loaded outline with {len(outline)} chapters")
    elif not use_fixed_outline: # Use ELIF and check NOT use_fixed_outline here # Changed from ELSE to ELIF
        # Only generate outline with LLM if NOT using fixed and NOT using custom outline
        print("--- DEBUG: Proceeding to LLM Outline Generation ---")  # Updated debug message
        print("--- DEBUG: Custom outline path condition is FALSE - Generating outline automatically with LLM ---")  # DEBUG message updated
        logger.info("No custom outline provided - generating outline automatically.")
        llm_config = settings.get_llm_config()
        print("--- llm_config obtained in main.py ---")
        print("--- Before OutlineGenerator ---")
        outline_gen = OutlineGenerator(agents, llm_config)  # 'agents' is now defined BEFORE OutlineGenerator
        print("--- After OutlineGenerator ---")
        print("--- Before generate_outline ---")
        outline = outline_gen.generate_outline(initial_prompt, num_chapters)
        print("--- After generate_outline ---")
        if not outline:
            logger.error("Outline generation failed.")
            return

    # Create new agents with outline context and genre configuration (now using book_agents, not outline_agents)
    book_agents = BookAgents(settings.llm, outline, genre_config)  # Re-create BookAgents with outline
    agents_with_context = book_agents.create_agents(initial_prompt, num_chapters)  # Re-create agents with context

    # Use the new agents for book generation
    book_generator = BookGenerator(agents_with_context, settings.get_llm_config(), outline)
    print("--- BookGenerator created in main.py ---")

    # Start book generation process
    print("--- Starting book generation in main.py ---")
    book_generator.generate_book(outline)
    print("--- Book generation process finished in main.py ---")

    print("--- main() function in main.py finished ---")


if __name__ == "__main__":
    main()