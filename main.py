"""Main script for running the book generation system - now with SIGTERM signal handling"""
import litellm   # ADD THIS LINE
litellm.set_verbose = True  # ADD THIS LINE
import os
import logging
from logging.config import dictConfig
from config import get_settings
import signal  # Import signal module
import sys  # Import sys module for exit

# Configure logging
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

dictConfig(logging_config)
logger = logging.getLogger(__name__)
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator
from llm.deepseek_client import DeepSeekClient

# Global flag to signal stop generation
stop_book_generation = False

def signal_handler(sig, frame):
    """Signal handler to catch SIGTERM and set stop flag"""
    global stop_book_generation
    print("\nStopping book generation process...")  # Indicate stop signal received
    stop_book_generation = True
    sys.exit(0)  # Gracefully exit after setting flag

# Register signal handler
signal.signal(signal.SIGTERM, signal_handler)

# Initialize DeepSeek client with configuration
settings = get_settings()
llm_config = settings.get_llm_config()
deepseek_client = DeepSeekClient(config=llm_config)

def load_custom_outline(outline_path):
    """Load a custom outline from file"""
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
    """Main function to run book generation - now with stop signal handling"""
    global stop_book_generation  # Use the global flag

    # Check if genre is selected
    genre = os.getenv('BOOK_GENRE')
    if not genre:
        print("No genre selected. Please run './select_genre.py' first to choose a genre.")
        print("Example: ./select_genre.py")
        return

    # Get base configuration
    settings = get_settings()

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
        if model_type in model_lower and not getattr(settings.llm, key_name, None):
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
    outline = None
    if custom_outline_path and os.path.exists(custom_outline_path):
        logger.info(f"Loading custom outline from: {custom_outline_path}")
        outline = load_custom_outline(custom_outline_path)
        if not outline:
            logger.error("Failed to load custom outline, please check the format")
            return
        logger.info(f"Successfully loaded outline with {len(outline)} chapters")
    else:
        logger.error(f"Custom outline not found at: {custom_outline_path}")
        return

    # Display startup information and wait for user confirmation
    display_startup_info(genre_config, outline)

    # Initial prompt for the book
    initial_prompt = """
    Create a story in my established writing style with these key elements:
    It's important that it has several key storylines that intersect and influence each other.
    The story should be set in a modern corporate environment, with a focus on technology and finance.
    The protagonist is a software engineer named Dane who has just completed a groundbreaking stock prediction algorithm.
    The algorithm predicts a catastrophic market crash, but Dane oversleeps and must rush to an important presentation
    to share his findings with executives. The tension arises from the questioning of whether his "error" might actually be correct.

    The piece is written in third-person limited perspective, following Dane's thoughts and experiences.
    The prose is direct and technical when describing the protagonist's work, but becomes more introspective
    during personal moments. The author employs a mix of dialogue and internal monologue, with particular
    attention to time progression and technical details around the algorithm and stock predictions.

    Story Arch:
    - Setup: Dane completes a groundbreaking stock prediction algorithm late at night
    - Initial Conflict: The algorithm predicts a catastrophic market crash
    - Rising Action: Dane oversleeps and must rush to an important presentation
    - Climax: The presentation to executives where he must explain his findings
    - Tension Point: The questioning of whether his "error" might actually be correct

    Characters:
    - Dane: The protagonist; a dedicated software engineer who prioritizes work over personal life.
      Wears grey polo shirts on Thursdays, tends to get lost in his work, and struggles with work-life balance.
      More comfortable with code than public speaking.
    - Gary: Dane's nervous boss who seems caught between supporting Dane and managing upper management's expectations
    - Jonathan Morego: Senior VP of Investor Relations who raises pointed questions about the validity of Dane's predictions
    - Silence: Brief mention as an Uber driver
    - C-Level Executives: Present as an audience during the presentation

    World Description:
    The story takes place in a contemporary corporate setting, likely a financial technology company.
    The world appears to be our modern one, with familiar elements like:
    - Major tech companies (Tesla, Google, Apple, Microsoft)
    - Stock market and financial systems
    - Modern technology (neural networks, predictive analytics)
    - Urban environment with rideshare services like Uber
    - Corporate hierarchy and office culture

    The story creates tension between the familiar corporate world and the potential for an unprecedented
    financial catastrophe, blending elements of technical thriller with workplace drama. The setting feels
    grounded in reality but hints at potentially apocalyptic economic consequences.
    """

    num_chapters = settings.generation.max_chapters
    # Create agents with genre configuration
    outline_agents = BookAgents(settings.llm, genre_config=genre_config)
    agents = outline_agents.create_agents(initial_prompt, num_chapters)

    # Generate the outline if not using custom one
    if not outline:
        llm_config = settings.get_llm_config()
        outline_gen = OutlineGenerator(agents, llm_config)
        logger.info("Generating book outline...")
        outline = outline_gen.generate_outline(initial_prompt, num_chapters)

    # Create new agents with outline context and genre configuration
    book_agents = BookAgents(settings.llm, outline, genre_config)
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
    if outline:
        for chapter in outline:
            if stop_book_generation:  # Check stop flag at chapter start
                print("Book generation interrupted by user.")  # Indicate interruption
                break  # Exit chapter loop if stop flag is set

            chapter_number = chapter["chapter_number"]

            # Verify previous chapter exists and is valid
            if chapter_number > 1:
                prev_file = os.path.join(book_output", f"chapter_{chapter_number - 1:02d}.txt") # Corrected path
                if not os.path.exists(prev_file):
                    logger.error(f"Previous chapter {chapter_number - 1} not found. Stopping.")
                    break

                with open(prev_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if not book_gen._verify_chapter_content(content, chapter_number - 1):
                        logger.error(f"Previous chapter {chapter_number - 1} content invalid. Stopping.")
                        break

            # Generate current chapter
            logger.info(f"Starting Chapter {chapter_number}")
            book_gen.generate_chapter(chapter_number, chapter["prompt"])

            # Verify current chapter
            chapter_file = os.path.join(book_gen.output_dir, f"chapter_{chapter_number:02d}.txt") # Corrected path
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