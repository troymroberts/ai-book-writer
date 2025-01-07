# AutoGen Book Generator

A Python-based system that uses AutoGen to generate complete books through collaborative AI agents. The system employs multiple specialized agents working together to create coherent, structured narratives from initial prompts.

## Features

- Multi-agent collaborative writing system
- Structured chapter generation with consistent formatting
- Maintains story continuity and character development
- Automated world-building and setting management
- Support for complex, multi-chapter narratives
- Built-in validation and error handling

## Architecture

The system uses several specialized agents:

- **Story Planner**: Creates high-level story arcs and plot points
- **World Builder**: Establishes and maintains consistent settings
- **Memory Keeper**: Tracks continuity and context
- **Writer**: Generates the actual prose
- **Editor**: Reviews and improves content
- **Outline Creator**: Creates detailed chapter outlines

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/autogen-book-generator.git
cd autogen-book-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Basic usage:
```python
from main import main

if __name__ == "__main__":
    main()
```

2. Validate LLM connection:
```python
from llm.factory import LLMFactory

# Test connection to configured LLM
if LLMFactory.test_connection():
    print("Connection successful!")
else:
    print("Connection failed. Check your configuration.")
```

## Writing Guide

For detailed instructions on creating book outlines and using the generator effectively, see the [Writing Guide](authors.md). This guide covers:
- Creating custom outlines
- Structuring chapters
- Using templates
- Configuring LLM settings
- Best practices for book generation

2. Custom initial prompt:

## Prompt Templates

The system supports template-based prompts for more structured generation. Templates allow you to define reusable prompt patterns with variables.

### Template Syntax

Templates use Python's format string syntax with named placeholders:
```
{placeholder_name}
```

Example template:
```
Write a story about {character} who lives in {location} and wants to {goal}.
```

### Using Templates

1. Create a template configuration:
```python
template = "Write a story about {character} who lives in {location} and wants to {goal}."
variables = {
    "character": "a young wizard",
    "location": "a magical forest",
    "goal": "find the lost artifact"
}
```

2. Use with LLM generation:
```python
from llm.factory import LLMFactory

llm = LLMFactory.create_llm(config)
result = llm.generate_with_template(template, variables)
```

### Template Validation

The system validates templates before use:
- All placeholders must have corresponding variables
- Template syntax must be valid
- Variables must be strings or convertible to strings

### Advanced Features

- Nested templates (templates within templates)
- Default values for optional variables
- Template inheritance and composition
- Automatic variable type conversion

2. Custom initial prompt:
```python
from config import get_config
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator

# Get configuration
agent_config = get_config()

# Create agents
outline_agents = BookAgents(agent_config)
agents = outline_agents.create_agents()

# Generate outline
outline_gen = OutlineGenerator(agents, agent_config)
outline = outline_gen.generate_outline(your_prompt, num_chapters=25)

# Initialize book generator
book_agents = BookAgents(agent_config, outline)
agents_with_context = book_agents.create_agents()
book_gen = BookGenerator(agents_with_context, agent_config, outline)

# Generate book
book_gen.generate_book(outline)
```

## Configuration

The system can be configured through `config.py` and environment variables. Key configurations include:

### General Settings
- OUTPUT_DIR: Directory for generated books (default: "./generated_books")
- MAX_TOKENS: Maximum length of generated text (default: 4096)
- TEMPERATURE: Controls creativity (0.0-1.0, default: 0.7)

### Generation Parameters
- MAX_CHAPTERS: Maximum number of chapters per book (default: 10)
- MIN_CHAPTER_LENGTH: Minimum words per chapter (default: 1000)
- MAX_CHAPTER_LENGTH: Maximum words per chapter (default: 5000)

### System Settings
- LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR, default: INFO)
- LOG_FILE: Log file location (default: "book_generator.log")

### Advanced Settings
- USE_GPU: Enable GPU acceleration if available (default: True)
- BATCH_SIZE: Number of parallel generations (default: 4)
- MEMORY_LIMIT: Maximum memory usage (0.0-1.0, default: 0.8)

### LLM Configuration
- LLM_TYPE: "local" or "litellm" (default: "local")
- LLM_MODEL: Model name with provider prefix (see below)
- LOCAL_LLM_URL: URL for local model (default: "http://localhost:1234/v1")
- LITELLM_API_BASE: Base URL for LiteLLM API
- LITELLM_API_VERSION: API version for LiteLLM

### Environment Variables
Set these in your environment or .env file:

1. Choose LLM Type:
```bash
# For local models
export LLM_TYPE=local
export LOCAL_LLM_URL=http://localhost:1234/v1

# For cloud models
export LLM_TYPE=litellm
export LITELLM_API_BASE=https://api.litellm.com  # Optional
export LITELLM_API_VERSION=v1  # Optional
```

2. Set Model and API Key:

For OpenAI models:
```bash
export LLM_MODEL="openai/gpt-4"  # or openai/gpt-3.5-turbo
export OPENAI_API_KEY="your-api-key"
```

For DeepSeek models:
```bash
export LLM_MODEL="deepseek/deepseek-coder"
export DEEPSEEK_API_KEY="your-api-key"
```

For Gemini models:
```bash
export LLM_MODEL="gemini/gemini-pro"
export GEMINI_API_KEY="your-api-key"
```

For Groq models:
```bash
export LLM_MODEL="groq/mixtral-8x7b-32768"
export GROQ_API_KEY="your-api-key"
```

For local models:
```bash
export LLM_MODEL="mistral-nemo-instruct-2407"  # No prefix needed for local models
```

3. Optional: Configure Fallback Models:
```bash
# Comma-separated list of fallback models
export LLM_FALLBACK_MODELS="openai/gpt-3.5-turbo,deepseek/deepseek-coder"
```

## Output Structure

Generated content is saved in the `book_output` directory:
```
book_output/
├── outline.txt
├── chapter_01.txt
├── chapter_02.txt
└── ...
```

## Requirements

- Python 3.8+
- AutoGen 0.2.0+
- Other dependencies listed in requirements.txt

## Development

To contribute to the project:

1. Fork the repository
2. Create a new branch for your feature
3. Install development dependencies:
```bash
pip install -r requirements.txt
```
4. Make your changes
5. Run tests:
```bash
pytest
```
6. Submit a pull request

### Release Process

The project uses semantic versioning (vMAJOR.MINOR.PATCH). To create a new release:

1. Ensure all changes are committed
2. Run the release script:
```bash
./tag_release.sh
```

This will:
- Automatically increment the patch version
- Create a new git tag
- Push the tag to the remote repository

For major or minor version bumps, manually edit the script to adjust the version number accordingly.

## Error Handling

The system includes robust error handling:
- Validates chapter completeness
- Ensures proper formatting
- Maintains backup copies of generated content
- Implements retry logic for failed generations

## Limitations

- Requires significant computational resources
- Generation time increases with chapter count
- Quality depends on the underlying LLM model
- May require manual review for final polish

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using the [AutoGen](https://github.com/microsoft/autogen) framework
- Inspired by collaborative writing systems
