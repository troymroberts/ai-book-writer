"""Main script for running the book generation system - now with SIGTERM signal handling"""
#!/usr/bin/env python3
print("--- main.py script started ---")
print("--- Initializing main.py logging ---")
import litellm
litellm.set_verbose = True
print("--- litellm.set_verbose = True executed ---")
import os
import logging
from logging.config import dictConfig
from config import get_settings
import signal
import sys

# Configure logging (simplified for brevity in this debug version - you can keep your full logging config if you prefer)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator

stop_book_generation = False

def signal_handler(sig, frame):
    global stop_book_generation
    print("\nStopping book generation process...")
    stop_book_generation = True
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)

def load_custom_outline(outline_path):
    try:
        with open(outline_path, "r") as f:
            content = f.read()
        # Parse the outline into chapter prompts
        chapters = []
        current_chapter = None

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("### Chapter"):
                if current_chapter:
                    chapters.append(current_chapter)
                # Extract chapter number and title
                title_parts = line.split(":", 1)
                if len(title_parts) > 1:
                    title = title_parts[1].strip()
                else:
                    title = line.replace("### ", "").strip()

                current_chapter = {
                    "title": title,
                    "prompt": "",
                    "chapter_number": len(chapters) + 1
                }
            elif line and current_chapter:
                # Skip divider lines
                if not line.startswith("---") and not line == "":
                    # Handle bullet points and other formatting
                    if line.startswith("- "):
                        line = line[2:]  # Remove bullet point
                    elif line.startswith("**") and line.endswith("**"):
                        line = line[2:-2]  # Remove bold markers
                    current_chapter["prompt"] += line + "\n"

        # Don't forget to add the last chapter
        if current_chapter:
            chapters.append(current_chapter)

        if not chapters:
            logger.error("No chapters found in outline")
            return None

        logger.info(f"Successfully loaded {len(chapters)} chapters from custom outline")
        return chapters
    except Exception as e:
        logger.error(f"Error loading custom outline: {e}")
        return None

def load_genre_config(genre_name=None):
    """Load genre-specific configuration"""
    if not genre_name:
        return {}

    # Handle genre templates in genre subdirectory
    config_path = f"config_templates/genre/{genre_name}.py"
    if not os.path.exists(config_path):
        # Try legacy location for backward compatibility
        legacy_path = f"config_templates/{genre_name}.py"
        if os.path.exists(legacy_path):
            config_path = legacy_path
        else:
            logger.warning(f"Genre configuration '{genre_name}' not found at {config_path}")
            return {}

    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("genre_config", config_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Extract all uppercase variables as configuration
        return {name: getattr(module, name) for name in dir(module)
                if name.isupper() and not name.startswith('_')}
    except Exception as e:
        logger.error(f"Error loading genre configuration: {e}")
        return {}

def apply_genre_config_to_agents(agents, genre_config):
    """Apply genre config to agents"""
    if not genre_config:
        return agents

    # Update writer's configuration
    if "writer" in agents:
        writer_msg = agents["writer"].system_message
        style_config = {
            "WRITING_STYLE": genre_config.get("WRITING_STYLE", "standard"),
            "NARRATIVE_STYLE": genre_config.get("NARRATIVE_STYLE", "third_person"),
            "PACING_SPEED": genre_config.get("PACING_SPEED", 0.7),
            "DESCRIPTIVE_DEPTH": genre_config.get("DESCRIPTIVE_DEPTH", 0.7)
        }
        writer_msg += f"\n\nStyle Configuration:\n{style_config}"
        agents["writer"].system_message = writer_msg

    # Update other agents as needed...
    return agents

def display_startup_info(genre_config, outline):
    """Display genre and outline information at startup"""
    print("\n=== Book Generation Configuration ===")

    genre = os.getenv('BOOK_GENRE')
    if genre:
        print(f"\nSelected Genre: {genre}")
        if genre_config:
            print(f"Writing Style: {genre_config.get('WRITING_STYLE', 'Standard')}")
            print(f"Narrative Style: {genre_config.get('NARRATIVE_STYLE', 'Third Person')}")
        else:
            print("Warning: Genre configuration not found - using default settings")
    else:
        print("\nNo specific genre selected - using default configuration")

    if outline:
        print("\nBook Outline:")
        for chapter in outline:
            print(f"\nChapter {chapter['chapter_number']}: {chapter['title']}")
            print("-" * 50)
            print(chapter['prompt'])
    else:
        print("\nNo outline available - will generate one")

    input("\nPress Enter to start book generation...")

def main():
    print("--- main() function in main.py started ---")
    global stop_book_generation

    # Check if genre is selected
    genre = os.getenv('BOOK_GENRE')
    print(f"--- BOOK_GENRE env var in main.py: {genre} ---")
    if not genre:
        print("No genre selected. Please run './select_genre.py' first to choose a genre.")
        print("Example: ./select_genre.py")
        return

    # Get base configuration
    settings = get_settings()
    print("--- Settings object created in main.py ---")

    # Validate API keys based on model requirements
    model_lower = settings.llm.model.lower()

    # Define model to API key requirements
    key_requirements = {
        "gpt": "openai_api_key",
        "claude": "anthropic_api_key",
        "command": "cohere_api_key",
        "huggingface": "huggingface_api_key",
        "litellm": "litellm_api_key",
        "deepseek": "deepseek_api_key",
        "gemini": "google_api_key",  # Gemini uses Google API key
        "groq": "groq_api_key"
    }

    # Check all required keys
    missing_keys = []
    for model_type, key_name in key_requirements.items():
        if model_type in model_lower and not model_lower.startswith("ollama/"): # Exclude ollama models from API key check
            if not getattr(settings.llm, key_name, None):
                missing_keys.append(key_name)

    if missing_keys:
        logger.error("The following API keys are required but not provided:")
        for key in missing_keys:
            logger.error(f"- {key}")
        return

    # Get genre configuration
    genre = os.getenv('BOOK_GENRE')
    genre_config = load_genre_config(genre)
    logger.debug(f"Loaded genre config: {genre_config}")

    # Check if using custom outline
    custom_outline_path = os.getenv('CUSTOM_OUTLINE')
    print(f"--- DEBUG: CUSTOM_OUTLINE environment variable value: '{custom_outline_path}' (Type: {type(custom_outline_path)}) ---") # DEBUGGING LINE

    outline = None
    if custom_outline_path and os.path.exists(custom_outline_path):
        print("--- DEBUG: Condition 'custom_outline_path and os.path.exists(custom_outline_path)' is TRUE ---") # DEBUGGING LINE
        logger.info(f"Loading custom outline from: {custom_outline_path}")
        outline = load_custom_outline(custom_outline_path)
        if not outline:
            logger.error("Failed to load custom outline, please check the format")
            return
        logger.info(f"Successfully loaded outline with {len(outline)} chapters")
    else:
        print("--- DEBUG: Condition 'custom_outline_path and os.path.exists(custom_outline_path)' is FALSE - Should generate outline ---") # DEBUGGING LINE
        logger.error(f"Custom outline not found at: {custom_outline_path}") # Keep this error log for now - but it should now be INFO level in normal operation
        # --- Outline generation code ---
        llm_config = settings.get_llm_config()
        print("--- llm_config obtained in main.py ---")
        outline_gen = OutlineGenerator(agents, llm_config)
        print("--- OutlineGenerator created in main.py ---")
        logger.info("Generating book outline...")
        outline = outline_gen.generate_outline(initial_prompt, num_chapters)
        print("--- Outline generated (or attempted) in main.py ---")
        if not outline:
            logger.error("Failed to generate outline.")
            return

    # Create agents with genre configuration (BookAgents now expects outline even if it's generated later)
    book_agents = BookAgents(settings.llm, outline, genre_config) # Pass outline here
    agents_with_context = book_agents.create_agents(initial_prompt, num_chapters)

    # Log genre configuration if available
    if genre_config:
        logger.debug("Using genre configuration: %s", genre)
        logger.debug("Style settings:")
        for key in ['WRITING_STYLE', 'NARRATIVE_STYLE', 'PACING_SPEED', 'DESCRIPTIVE_DEPTH']:
            if key in genre_config:
                logger.debug("- %s: %s", key, genre_config[key])

    # Initialize book generator with contextual agents
    llm_config = settings.get_llm_config()
    book_gen = BookGenerator(agents_with_context, llm_config, outline)

    # Log the generated outline
    logger.info("Generated Outline:")
    if outline: # Check if outline is not None before proceeding
        for chapter in outline:
            logger.info("\nChapter %d: %s", chapter['chapter_number'], chapter['title'])
            logger.info("-" * 50)
            logger.info(chapter['prompt'])

        # Save the outline for reference
        logger.info("Saving outline to file...")
        with open("book_output/outline.txt", "w") as f:
            for chapter in outline:
                f.write(f"\nChapter {chapter['chapter_number']}: {chapter['title']}\n")
                f.write("-" * 50 + "\n")
                f.write(chapter['prompt'] + "\n")

        # Generate the book using the outline - with stop signal check in loop
        logger.info("Generating book chapters...")
        if outline: # Re-check outline before chapter generation loop
            for chapter in outline:
                if stop_book_generation:  # Check stop flag at chapter start
                    print("Book generation interrupted by user.")
                    break  # Exit chapter loop if stop flag is set

                chapter_number = chapter["chapter_number"]

                # Verify previous chapter exists and is valid
                if chapter_number > 1:
                    prev_file = os.path.join("book_output", f"chapter_{chapter_number-1:02d}.txt")
                    if not os.path.exists(prev_file):
                        logger.error(f"Previous chapter {chapter_number-1} not found. Stopping.")
                        break

                    with open(prev_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if not book_gen._verify_chapter_content(content, chapter_number-1):
                            logger.error(f"Previous chapter {chapter_number-1} content invalid. Stopping.")
                            break

                # Generate current chapter
                logger.info(f"Starting Chapter {chapter_number}")
                book_gen.generate_chapter(chapter_number, chapter["prompt"])

                chapter_file = os.path.join(book_gen.output_dir, f"chapter_{chapter_number:02d}.txt")
                if not os.path.exists(chapter_file):
                    logger.error(f"Failed to generate chapter {chapter_number}")
                    break

                with open(chapter_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not book_gen._verify_chapter_content(content, chapter_number):
                        logger.error(f"Chapter {chapter_number} content invalid")
                        break

                logger.info(f"Chapter {chapter_number} complete")
                time.sleep(5)
    else:
        logger.error("No outline was generated - cannot generate book")


if __name__ == "__main__":
    main()