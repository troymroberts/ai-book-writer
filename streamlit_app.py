"""
Streamlit UI for AI Book Writer - WITH OLLAMA BASE URL INPUT IN UI
"""
import os
import streamlit as st
import ebooklib
from ebooklib import epub
from datetime import datetime
from pathlib import Path
import glob
import json
import markdown
import subprocess
import signal  # Import the signal module
from config.settings import Settings, LLMSettings
import logging
from logging.config import dictConfig
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator
import litellm  # Import litellm for listing ollama models

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session state initialization
if 'generation_status' not in st.session_state:
    st.session_state.generation_status = None
if 'current_chapter' not in st.session_state:
    st.session_state.current_chapter = 1
if 'preview_content' not in st.session_state:
    st.session_state.preview_content = ""
if 'process' not in st.session_state:  # To store the subprocess
    st.session_state.process = None
if 'stop_generation' not in st.session_state:  # Flag to control generation
    st.session_state.stop_generation = False
if 'ollama_models' not in st.session_state: # Store Ollama model list in session state
    st.session_state.ollama_models = []

def load_env_file():
    """Load and parse .env file"""
    env_dict = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip().strip('"')
    return env_dict

def save_env_file(env_dict):
    """Save environment variables to .env file"""
    with open('.env', 'w') as f:
        for key, value in env_dict.items():
            f.write(f'{key}="{value}"\n')

def create_epub(title, author, chapters_dir, output_path, cover_image=None):
    """Create EPUB book from generated chapters with enhanced features"""
    book = epub.EpubBook()

    # Set metadata
    book.set_identifier(f'ai-book-{datetime.now().strftime("%Y%m%d%H%M%S")}')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    # Add cover if provided
    if cover_image and os.path.exists(cover_image):
        book.set_cover("cover.jpg", open(cover_image, 'rb').read())

    # Add CSS
    style = '''
        body { margin: 5%; text-align: justify; font-size: 1em; }
        h1 { text-align: center; font-size: 2em; margin-bottom: 1em; }
        h2 { text-align: left; font-size: 1.5em; margin: 1em 0; }
        p { margin: 1em 0; line-height: 1.5; }
    '''
    nav_css = epub.EpubItem(uid="style", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # Add copyright page
    copyright_html = epub.EpubHtml(title='Copyright', file_name='copyright.xhtml')
    copyright_html.content = f'''
        <html><body>
        <h1>Copyright</h1>
        <p> {datetime.now().year} {author}</p>
        <p>All rights reserved. This book or any portion thereof may not be reproduced or used in any manner whatsoever without the express written permission of the publisher except for the use of brief quotations in a book review.</p>
        <p>Generated using AI Book Writer</p>
        <p>First Edition, {datetime.now().strftime("%B %Y")}</p>
        </body></html>
    '''
    book.add_item(copyright_html)

    # Add chapters
    chapters = []
    spine = ['nav', copyright_html]

    # Get all chapter files and sort them
    chapter_files = sorted(glob.glob(os.path.join(chapters_dir, 'chapter_*.txt')))

    for i, chapter_file in enumerate(chapter_files, 1):
        with open(chapter_file, 'r') as f:
            content = f.read()

        # Create chapter
        chapter = epub.EpubHtml(title=f'Chapter {i}', file_name=f'chapter_{i:02d}.xhtml')
        chapter.content = f'<h1>Chapter {i}</h1>\n' + markdown.markdown(content)
        chapter.add_item(nav_css)

        # Add chapter
        book.add_item(chapter)
        chapters.append(chapter)
        spine.append(chapter)

    # Create table of contents
    book.toc = [(epub.Section('Table of Contents'), chapters)]

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Set spine
    book.spine = spine

    # Create EPUB
    epub.write_epub(output_path, book)

def check_calibre_installed():
    """Check if Calibre's ebook-convert is available"""
    try:
        subprocess.run(['ebook-convert', '--version'],
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def export_to_pdf(epub_path, output_path):
    """Convert EPUB to PDF using Calibre's ebook-convert"""
    if not check_calibre_installed():
        st.error("""Calibre is not installed. To enable PDF export, please install Calibre.
   Please download from the official website:
   https://calibre-ebook.com/download_osx""")
        return False

    try:
        subprocess.run(['ebook-convert', epub_path, output_path], check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error converting to PDF: {e}")
        return False

def preview_chapter(chapter_path):
    """Preview chapter content with formatting"""
    try:
        with open(chapter_path, 'r') as f:
            content = f.read()
        return markdown.markdown(content)
    except Exception as e:
        return f"Error loading chapter: {str(e)}"

def get_ollama_models():
    """Lists models available in Ollama using litellm"""
    try:
        response = litellm.ollama_list_models()
        if response and response.get('models'):
            return [model['name'] for model in response['models']]
        else:
            return []
    except Exception as e:
        logger.error(f"Error listing Ollama models: {e}")
        return []

def main():
    st.set_page_config(page_title="AI Book Writer", layout="wide")
    st.title("AI Book Writer")

    # Load current environment variables
    env_dict = load_env_file()

    # Initialize settings
    settings = Settings()

    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Configuration", "Book Generation", "Preview & Export"])

    with tab1:
        # Sidebar for configuration
        st.header("Configuration")

        # LLM Provider Type Selection
        provider_type_options = ["DeepSeek", "OpenAI", "Gemini", "Groq", "Ollama"]
        selected_provider_type = st.selectbox(
            "Select LLM Provider Type",
            provider_type_options,
            index=provider_type_options.index(env_dict.get('LLM__PROVIDER_TYPE', 'DeepSeek')) if env_dict.get('LLM__PROVIDER_TYPE') in provider_type_options else 0,
            help="Choose the type of LLM provider you want to use (e.g., DeepSeek API, OpenAI API, Google Gemini API, Groq API, or local Ollama).",
        )

        # Model selection - Dynamic options based on provider type
        model_options = []
        if selected_provider_type == "Ollama":
            if not st.session_state.ollama_models: # Load models only once per session
                st.session_state.ollama_models = get_ollama_models()
            model_options = st.session_state.ollama_models
        elif selected_provider_type == "DeepSeek":
            model_options = ['deepseek-chat', 'deepseek-reasoner']
        elif selected_provider_type == "OpenAI":
            model_options = ['gpt-4', 'gpt-3.5-turbo']
        elif selected_provider_type == "Gemini":
            model_options = ['gemini-pro']
        elif selected_provider_type == "Groq":
            model_options = ['llama2-70b-4096']

        selected_model = st.selectbox(
            "Select Model",
            model_options if model_options else ["Please select provider type first"], # Placeholder if no options
            index=0 if model_options else 0,
            disabled=not model_options, # Disable if no model options loaded
            help="Select the specific LLM model to use from the chosen provider. The list of models is dynamically updated based on the selected provider type. For Ollama, this list is populated from your local Ollama server."
        )

        # API Configuration / Ollama Base URL - Conditional Input
        if selected_provider_type == "Ollama":
            ollama_base_url = st.text_input(
                "Ollama Base URL",
                value=env_dict.get('OLLAMA_BASE_URL', 'http://localhost:11434'), # Default value
                help="Enter the base URL of your Ollama server if it's running on a non-default address. Default is http://localhost:11434."
            )
            api_key = None # No API key for Ollama
            test_api_key_button = False # No API key test button for Ollama
        else:
            ollama_base_url = None # Not used for other providers
            api_key_label = f"{selected_provider_type} API Key"
            api_key_col, test_button_col = st.columns([3, 1])  # Create columns for layout

            with api_key_col:
                api_key = st.text_input(
                    api_key_label,
                    f"Enter your {selected_provider_type} API Key",  # Dynamic label
                    value=env_dict.get(f'LLM__API_KEY_{selected_provider_type.upper()}', ''), # Dynamic env var
                    type="password",
                    help=f"Enter your API key for {selected_provider_type}. You can obtain API keys from the {selected_provider_type} developer portal. Keep your API key secure."
                )
            with test_button_col:
                st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)  # Add vertical space
                test_api_key_button = st.button("Test API Key", key=f"test_api_key_{selected_provider_type}", help="Test API key connectivity for selected provider.") # Unique key


        # Test API Key Button Logic - Conditional for non-Ollama providers
        if selected_provider_type != "Ollama" and test_api_key_button:
            with st.spinner(f"Testing {selected_provider_type} API Key..."):
                from llm.factory import LLMFactory  # Import LLMFactory here
                test_config = {
                    'model': selected_model,
                    'api_key': api_key
                }
                if LLMFactory.test_connection(test_config):
                    st.success(f"{selected_provider_type} API key test successful!")
                else:
                    st.error(f"{selected_provider_type} API key test failed. Please check your key and model selection.")


        # Genre selection, Book metadata, Generation parameters, Save Configuration Button ( ... rest of your existing tab1 code - unchanged ... )
        # ... (rest of tab1 code - unchanged - paste from previous version) ...
        # Save configuration button
        if st.button("Save Configuration"):
            env_dict.update({
                'LLM__MODEL': f"{selected_provider_type.lower()}/{selected_model}" if selected_provider_type == "Ollama" else selected_model, # Save ollama model with prefix
                'LLM__PROVIDER_TYPE': selected_provider_type, # Save provider type
                'LLM__DEEPSEEK_API_KEY': api_key if selected_provider_type == "DeepSeek" else env_dict.get('LLM__DEEPSEEK_API_KEY', ''), # Conditionally save API keys
                'OLLAMA_BASE_URL': ollama_base_url if selected_provider_type == "Ollama" else env_dict.get('OLLAMA_BASE_URL', 'http://localhost:11434'), # Save Ollama base URL
                # ... (rest of your existing save config logic - unchanged) ...
                'BOOK_GENRE': f'genre/{selected_genre}',
                'GEN_MAX_TOKENS': str(max_tokens),
                'GEN_TEMPERATURE': str(temperature)
            })
            save_env_file(env_dict)
            st.success("Configuration saved!")


    with tab2:
        st.header("Book Generation")
        # ... (rest of your tab2, tab3 code - unchanged - paste from previous version) ...


    with tab3:
        st.header("Preview & Export")
        # ... (rest of your tab3 code - unchanged - paste from previous version) ...


def generate_book_process(api_key, progress_bar, status_text_area): # ... (rest of your generate_book_process function - unchanged - paste from previous version) ...
    # ... (rest of your generate_book_process function - unchanged) ...


if __name__ == "__main__":
    main()