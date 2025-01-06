"""Main script for running the book generation system"""
import os
from config import get_config
"""Main script for running the book generation system"""
from config import get_config, MAX_CHAPTERS
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator

def load_custom_outline(outline_path):
    """Load a custom outline from file"""
    try:
        with open(outline_path, "r") as f:
            content = f.read()
        # Parse the outline into chapter prompts
        chapters = []
        current_chapter = None
        for line in content.split("\n"):
            if line.startswith("Chapter"):
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {
                    "title": line.split(":")[1].strip(),
                    "prompt": "",
                    "chapter_number": len(chapters) + 1
                }
            elif line.strip() and current_chapter:
                current_chapter["prompt"] += line + "\n"
        if current_chapter:
            chapters.append(current_chapter)
        return chapters
    except Exception as e:
        print(f"Error loading custom outline: {e}")
        return None

def main():
    # Get configuration
    agent_config = get_config()

    # Validate API keys based on model requirements
    if agent_config.get("model"):
        model_lower = agent_config["model"].lower()
        
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
            if model_type in model_lower and not agent_config.get(key_name):
                missing_keys.append(key_name)
        
        if missing_keys:
            print("Error: The following API keys are required but not provided:")
            for key in missing_keys:
                print(f"- {key}")
            return

    # Check if using custom outline
    custom_outline_path = os.getenv('CUSTOM_OUTLINE')
    if custom_outline_path:
        print("Loading custom outline...")
        outline = load_custom_outline(custom_outline_path)
        if not outline:
            print("Failed to load custom outline, using default generation")
            outline = None
    else:
        outline = None
"""Main script for running the book generation system"""
from config import get_config
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator

def load_custom_outline(outline_path):
    """Load a custom outline from file"""
    try:
        with open(outline_path, "r") as f:
            content = f.read()
        # Parse the outline into chapter prompts
        chapters = []
        current_chapter = None
        for line in content.split("\n"):
            if line.startswith("Chapter"):
                if current_chapter:
                    chapters.append(current_chapter)
                current_chapter = {
                    "title": line.split(":")[1].strip(),
                    "prompt": "",
                    "chapter_number": len(chapters) + 1
                }
            elif line.strip() and current_chapter:
                current_chapter["prompt"] += line + "\n"
        if current_chapter:
            chapters.append(current_chapter)
        return chapters
    except Exception as e:
        print(f"Error loading custom outline: {e}")
        return None

def main():
    # Get configuration
    agent_config = get_config()

    # Check if using custom outline
    if agent_config.get("custom_outline"):
        print("Loading custom outline...")
        outline = load_custom_outline(agent_config["custom_outline"])
        if not outline:
            print("Failed to load custom outline, using default generation")
            outline = None
    else:
        outline = None

    # Initial prompt for the book
    initial_prompt = """
    Create a story in my established writing style with these key elements:
    Its important that it has several key storylines that intersect and influence each other. The story should be set in a modern corporate environment, with a focus on technology and finance. The protagonist is a software engineer named Dane who has just completed a groundbreaking stock prediction algorithm. The algorithm predicts a catastrophic market crash, but Dane oversleeps and must rush to an important presentation to share his findings with executives. The tension arises from the questioning of whether his "error" might actually be correct.

    The piece is written in third-person limited perspective, following Dane's thoughts and experiences. The prose is direct and technical when describing the protagonist's work, but becomes more introspective during personal moments. The author employs a mix of dialogue and internal monologue, with particular attention to time progression and technical details around the algorithm and stock predictions.
    Story Arch:

    Setup: Dane completes a groundbreaking stock prediction algorithm late at night
    Initial Conflict: The algorithm predicts a catastrophic market crash
    Rising Action: Dane oversleeps and must rush to an important presentation
    Climax: The presentation to executives where he must explain his findings
    Tension Point: The questioning of whether his "error" might actually be correct

    Characters:

    Dane: The protagonist; a dedicated software engineer who prioritizes work over personal life. Wears grey polo shirts on Thursdays, tends to get lost in his work, and struggles with work-life balance. More comfortable with code than public speaking.
    Gary: Dane's nervous boss who seems caught between supporting Dane and managing upper management's expectations
    Jonathan Morego: Senior VP of Investor Relations who raises pointed questions about the validity of Dane's predictions
    Silence: Brief mention as an Uber driver
    C-Level Executives: Present as an audience during the presentation

    World Description:
    The story takes place in a contemporary corporate setting, likely a financial technology company. The world appears to be our modern one, with familiar elements like:

    Major tech companies (Tesla, Google, Apple, Microsoft)
    Stock market and financial systems
    Modern technology (neural networks, predictive analytics)
    Urban environment with rideshare services like Uber
    Corporate hierarchy and office culture

    The story creates tension between the familiar corporate world and the potential for an unprecedented financial catastrophe, blending elements of technical thriller with workplace drama. The setting feels grounded in reality but hints at potentially apocalyptic economic consequences.
    """

    num_chapters = MAX_CHAPTERS
    # Create agents
    outline_agents = BookAgents(agent_config)
    agents = outline_agents.create_agents(initial_prompt, num_chapters)
    
    # Generate the outline if not using custom one
    if not outline:
        outline_gen = OutlineGenerator(agents, agent_config)
        print("Generating book outline...")
        outline = outline_gen.generate_outline(initial_prompt, num_chapters)
    
    # Create new agents with outline context
    book_agents = BookAgents(agent_config, outline)
    agents_with_context = book_agents.create_agents(initial_prompt, num_chapters)
    
    # Initialize book generator with contextual agents
    book_gen = BookGenerator(agents_with_context, agent_config, outline)
    
    # Print the generated outline
    print("\nGenerated Outline:")
    for chapter in outline:
        print(f"\nChapter {chapter['chapter_number']}: {chapter['title']}")
        print("-" * 50)
        print(chapter['prompt'])
    
    # Save the outline for reference
    print("\nSaving outline to file...")
    with open("book_output/outline.txt", "w") as f:
        for chapter in outline:
            f.write(f"\nChapter {chapter['chapter_number']}: {chapter['title']}\n")
            f.write("-" * 50 + "\n")
            f.write(chapter['prompt'] + "\n")
    
    # Generate the book using the outline
    print("\nGenerating book chapters...")
    if outline:
        book_gen.generate_book(outline)
    else:
        print("Error: No outline was generated.")

if __name__ == "__main__":
    main()
