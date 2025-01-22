#!/bin/bash

# Check for .env file
if [ ! -f .env ]; then
    echo "Error: .env file not found"
    echo "Please copy env.example to .env and set your configuration:"
    echo "cp env.example .env"
    exit 1
fi

source .venv/bin/activate
pip install -r requirements.txt
source .env

# Check if LLM__MODEL is set
if [ -z "$LLM__MODEL" ]; then
    echo "Error: LLM__MODEL not set in .env file"
    echo "Please set LLM__MODEL in your .env file. Available models:"
    echo "- mistral-nemo-instruct-2407 (local)"
    echo "- openai/gpt-4, openai/gpt-3.5-turbo"
    echo "- deepseek/deepseek-chat"
    echo "- gemini/gemini-pro"
    echo "- groq/llama2-70b-4096"
    echo "- gemini-flash/gemini-flash"
    exit 1
fi

# Load genre from .env
if [ -z "$BOOK_GENRE" ]; then
    echo "Error: BOOK_GENRE not set in .env file"
    echo "Please set BOOK_GENRE in your .env file"
    exit 1
fi

# Check for custom outline
CUSTOM_OUTLINE="book_output/custom_outline.txt"
if [ ! -f "$CUSTOM_OUTLINE" ]; then
    echo "Error: Custom outline not found at $CUSTOM_OUTLINE"
    exit 1
fi

echo "=== Book Generation Configuration ==="
echo "LLM_MODEL=${LLM__MODEL}"
echo "Selected Genre: ${BOOK_GENRE}"
echo "Using Custom Outline: ${CUSTOM_OUTLINE}"
echo "Using DeepSeek API"
python -c "import os; print(f'Python sees LLM_MODEL as: {os.getenv(\"LLM__MODEL\")}')"
export CUSTOM_OUTLINE
python main.py
