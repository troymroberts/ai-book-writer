#!/bin/bash
source .venv/bin/activate
pip install -r requirements.txt
source .env

# Genre selection
echo "Available genres:"
ls config_templates/genre/ | sed 's/.py//g'
read -p "Enter genre name: " SELECTED_GENRE
export BOOK_GENRE=${SELECTED_GENRE}

echo "=== Book Generation Configuration ==="
echo "LLM_MODEL=${LLM_MODEL}"
echo "Selected Genre: ${BOOK_GENRE}"
echo "Using DeepSeek API"
python -c "import os; print(f'Python sees LLM_MODEL as: {os.getenv(\"LLM_MODEL\")}')"
export CUSTOM_OUTLINE="book_output/custom_outline.txt"
python main.py
