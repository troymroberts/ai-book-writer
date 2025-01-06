# AutoGen Book Generator - Beginner's Guide

Welcome to the AutoGen Book Generator project! This guide will help you get started with setting up and running the project.

## System Requirements

- Python 3.8 or higher
- 8GB RAM (16GB recommended)
- 10GB free disk space
- Git (for version control)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/autogen-book-generator.git
cd autogen-book-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The project supports both local models (Mistral-Nemo-Instruct-2407) and cloud-based models through LiteLLM. Choose your preferred setup:

### Option 1: Local Mistral-Nemo-Instruct-2407

1. Download the model weights and place them in your preferred location
2. Open `config.py` and set:
```python
LLM_TYPE = "local"
LLM_PATH = "/path/to/mistral-nemo-instruct-2407"
```

### Option 2: LiteLLM (OpenAI or other providers)

1. Install additional requirements:
```bash
pip install litellm
```

2. Set your API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key"
```

3. Open `config.py` and set:
```python
LLM_TYPE = "litellm"
LLM_MODEL = "gpt-3.5-turbo"  # or "gpt-4"
```

### Common Settings

Both configurations share these common settings:
- `OUTPUT_DIR`: Where generated books are saved
- `MAX_TOKENS`: Controls book length (default: 4096)
- `TEMPERATURE`: Adjusts creativity level (0.7-1.0 recommended)

### Troubleshooting

#### Local Model Issues
- Ensure model weights are accessible
- Verify sufficient system resources
- Check CUDA installation if using GPU

#### LiteLLM Issues
- Verify API key is set correctly
- Check internet connection
- Monitor API usage limits

## Running the Generator

1. Start the book generation:
```bash
python main.py
```

2. Follow the on-screen prompts to:
- Select book type (fiction/non-fiction)
- Choose genre
- Set length parameters
- Provide initial ideas

## Common Commands

- Generate a new book:
```bash
python main.py --new
```

- Continue an existing book:
```bash
python main.py --continue <book_id>
```

- View help:
```bash
python main.py --help
```

## Troubleshooting

### Installation Issues
- Ensure Python 3.8+ is installed
- Verify virtual environment activation
- Check internet connection for dependencies

### Generation Problems
- Verify LLM configuration
- Check available disk space
- Ensure sufficient system resources

### Common Errors
- "Module not found": Reinstall requirements
- "LLM not responding": Check LLM configuration
- "Memory error": Reduce generation parameters

## Next Steps

- Explore the [development documentation](development.md)
- Check out the [architecture diagrams](development.md#architectural-proposals)
- Review the [testing guidelines](development.md#testing-architecture)

## Additional Resources

- [AutoGen Framework Documentation](https://microsoft.github.io/autogen/)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Git Basics](https://git-scm.com/doc)

## Getting Help

For additional support:
- Open an issue on GitHub
- Check the project's FAQ section
- Join our community forum

Happy book generating!
