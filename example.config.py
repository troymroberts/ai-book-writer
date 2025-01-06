# Example Configuration File
# Copy this to config.py and modify as needed

# LLM Configuration
LLM_TYPE = "local"  # Options: "local" or "litellm"
LLM_PATH = "/path/to/your/model"  # Required for local models
LLM_MODEL = "gpt-3.5-turbo"  # Required for LiteLLM (e.g., "gpt-3.5-turbo", "gpt-4")

# Example Local Configuration
# LLM_TYPE = "local"
# LLM_PATH = "/models/mistral-nemo-instruct-2407"

# Example LiteLLM Configuration
# LLM_TYPE = "litellm"
# LLM_MODEL = "gpt-4"

# Output Settings
OUTPUT_DIR = "./generated_books"  # Where generated books are saved
MAX_TOKENS = 4096  # Maximum length of generated text
TEMPERATURE = 0.7  # Controls creativity (0.0-1.0)

# Generation Parameters
MAX_CHAPTERS = 10  # Maximum number of chapters per book
MIN_CHAPTER_LENGTH = 1000  # Minimum words per chapter
MAX_CHAPTER_LENGTH = 5000  # Maximum words per chapter

# System Settings
LOG_LEVEL = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_FILE = "book_generator.log"  # Log file location

# Advanced Settings
USE_GPU = True  # Enable GPU acceleration if available
BATCH_SIZE = 4  # Number of parallel generations
MEMORY_LIMIT = 0.8  # Maximum memory usage (0.0-1.0)
