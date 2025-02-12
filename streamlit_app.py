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

# Enable verbose logging for litellm - ADDED HERE!
litellm.set_verbose = True

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

    # Print environment variables for debugging - ADDED HERE
    print("\n--- Environment Variables Seen by Streamlit App ---")
    for key, value in os.environ.items():
        if key.startswith("LLM") or key.startswith("OLLAMA") or key.startswith("BOOK") or key.startswith("GEN"): # Filter for relevant env vars
            print(f"{key}={value}")
    print("---\n")

    # Initialize settings
    print("Environment LLM__MODEL:", os.environ.get('LLM__MODEL')) # <-- Add this
    settings = Settings()
    print("Settings LLM Model:", settings.llm.model) # <-- Add this

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
            # No dynamic model listing for Ollama anymore
            pass # We will use text input instead
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
            model_options if model_options and selected_provider_type != "Ollama" else ["Please select provider type first"], # Placeholder if no options, or if not Ollama
            index=0 if model_options and env_dict.get('LLM__MODEL') in model_options and selected_provider_type != "Ollama" else 0, # Set index only if model_options is not empty and env model is valid and not Ollama
            disabled=not model_options and selected_provider_type != "Ollama", # Disable if no model options loaded and not Ollama
            help="Select the specific LLM model to use from the chosen provider. The list of models is dynamically updated based on the selected provider type. For Ollama, enter model name manually."
        )

        if selected_provider_type == "Ollama":
            selected_model = st.text_input(
                "Ollama Model Name",
                value=env_dict.get('LLM__MODEL', '').split(':')[-1] if env_dict.get('LLM__MODEL', '').startswith('ollama/') else env_dict.get('LLM__MODEL', 'deepseek-r1:14b'), # Default value or extract from env, default to deepseek-r1:14b
                help="Enter the name of the Ollama model you want to use (e.g., llama2, mistral, deepseek-r1:14b). Ensure this model is available in your local Ollama server."
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
                    label=api_key_label, # Use keyword argument for label
                    placeholder=f"Enter your {selected_provider_type} API Key", # Use placeholder for the hint text
                    value=env_dict.get(f'LLM__API_KEY_{selected_provider_type.upper()}', ''), # Keyword argument for value
                    type="password",
                    help=f"Enter your {selected_provider_type}. You can obtain API keys from the {selected_provider_type} developer portal. Keep your API key secure."
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


        # Genre selection
        genre_options = [
            "literary_fiction", "fantasy_scifi", "thriller_mystery", "romance",
            "historical_fiction", "young_adult", "mysticism", "esoteric_philosophy",
            "comparative_religion", "consciousness_studies",
            "computer_science_textbook", "physics_textbook", "chemistry_textbook",
            "mathematics_textbook", "engineering_textbook"
        ]
        selected_genre = st.selectbox("Select Genre", genre_options, index=genre_options.index(env_dict.get('BOOK_GENRE', 'literary_fiction').replace("genre/","")) if env_dict.get('BOOK_GENRE') else 0, help="Choose the genre for your book. This affects the writing style and themes.")

        # Book metadata inputs
        book_title = st.text_input("Book Title", value=env_dict.get('BOOK_TITLE', 'My AI Book'), help="Enter the title of your book.")
        book_author = st.text_input("Author Name", value=env_dict.get('BOOK_AUTHOR', 'AI Author'), help="Enter the author name for the book.")
        cover_image_path = st.text_input("Cover Image Path (optional)", value=env_dict.get('BOOK_COVER_IMAGE', ''), help="Path to a cover image for the book (optional).")

        # Generation parameters
        max_tokens = st.slider("Max Tokens per Chapter", min_value=500, max_value=7000, value=int(env_dict.get('GEN_MAX_TOKENS', 4000)), step=100, help="Set the maximum number of tokens (words/word pieces) to generate per chapter.")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=float(env_dict.get('GEN_TEMPERATURE', 0.7)), step=0.05, help="Controls the randomness of the AI's output. Higher values (closer to 1) make the output more random and creative, while lower values (closer to 0) make it more focused and deterministic.")

        # Save configuration button
        if st.button("Save Configuration"):
            # Correctly save LLM_MODEL - preserve full ollama/model_name
            llm_model_value = f"ollama/{selected_model}" if selected_provider_type == "Ollama" else selected_model

            env_dict.update({
                'LLM__MODEL': llm_model_value,
                'LLM__PROVIDER_TYPE': selected_provider_type,
                'LLM__DEEPSEEK_API_KEY': api_key if selected_provider_type == "DeepSeek" else env_dict.get('LLM__DEEPSEEK_API_KEY', ''),
                'OLLAMA_BASE_URL': ollama_base_url if selected_provider_type == "Ollama" else env_dict.get('OLLAMA_BASE_URL', 'http://localhost:11434'),
                'BOOK_GENRE': f'genre/{selected_genre}',
                'BOOK_TITLE': book_title,
                'BOOK_AUTHOR': book_author,
                'BOOK_COVER_IMAGE': cover_image_path,
                'GEN_MAX_TOKENS': str(max_tokens),
                'GEN_TEMPERATURE': str(temperature)
            })
            save_env_file(env_dict)
            st.success("Configuration saved!")


    with tab2:
        st.header("Book Generation")
        col1, col2 = st.columns([3, 1])

        with col1:
            initial_prompt_text = st.text_area("Initial Book Prompt", value=env_dict.get('INITIAL_BOOK_PROMPT', 'Write a book about a dystopian future where AI controls society.'))
            num_chapters = st.number_input("Number of Chapters", min_value=5, max_value=30, value=int(env_dict.get('NUM_CHAPTERS', 10)), step=1, help="Set the number of chapters for your book.")
            custom_outline = st.text_area("Custom Outline (Optional, overrides genre template)") # <-- ADDED CUSTOM OUTLINE INPUT
            if st.button("Generate Book"):
                print("\n--- Generate Book Button Clicked ---") # ADD THIS LINE
                api_key = env_dict.get('LLM__DEEPSEEK_API_KEY') # Example for DeepSeek, adjust as needed

                if not api_key and selected_provider_type != "Ollama": # <-- Adjusted API key check
                    st.error("Please enter your API key in the Configuration tab.") # <-- More informative message
                    print("Error: API key missing or provider is not Ollama") # Log error to console too
                    return

                # Save custom outline if provided
                if custom_outline:
                    os.makedirs('book_output', exist_ok=True)
                    with open('book_output/custom_outline.txt', 'w') as f:
                        f.write(custom_outline)
                    os.environ['CUSTOM_OUTLINE'] = "book_output/custom_outline.txt" # Set env var for custom outline
                    print(f"Custom outline saved to book_output/custom_outline.txt and CUSTOM_OUTLINE env var set") # Log custom outline saving
                else:
                    os.environ.pop('CUSTOM_OUTLINE', None) # Ensure custom outline env var is unset if no custom outline provided
                    print("CUSTOM_OUTLINE environment variable unset (using generated outline)") # Log outline type

                st.session_state.generation_status = "Generating Outline"
                st.session_state.current_chapter = 1
                st.session_state.preview_content = ""
                st.session_state.stop_generation = False  # Reset stop flag
                env_dict['INITIAL_BOOK_PROMPT'] = initial_prompt_text
                env_dict['NUM_CHAPTERS'] = str(num_chapters)
                save_env_file(env_dict)

                # Prepare and start book generation process
                progress_bar = st.progress(0)
                status_text_area = st.empty()
                print("Before subprocess.Popen (direct main.py)") # Updated print message
                st.session_state.process = subprocess.Popen(
                    ["./venv/bin/python", "main.py"],  # Run main.py directly
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    env={**os.environ.copy(),  # Inherit existing env vars and add/override:
                         "LLM__MODEL": env_dict.get('LLM__MODEL'), # Pass LLM_MODEL
                         "BOOK_GENRE": env_dict.get('BOOK_GENRE'), # Pass BOOK_GENRE
                         "OLLAMA_BASE_URL": env_dict.get('OLLAMA_BASE_URL', 'http://localhost:11434'), # Pass Ollama URL
                         "CUSTOM_OUTLINE": os.environ.get('CUSTOM_OUTLINE', '') # Pass CUSTOM_OUTLINE if set, otherwise empty
                         },
                    preexec_fn=os.setsid,
                    cwd=os.getcwd()
                )
                print("After subprocess.Popen (direct main.py)") # Updated print message
                st.session_state.generation_status = "Generating Book Content"
                print("--- End Generate Book Button Clicked ---\n") # ADD THIS LINE


        with col2:
            st.markdown("### Generation Status")
            status_display = st.empty()
            chapter_display = st.empty()
            stop_button_col = st.columns(1) # Create column layout for button

            if st.session_state.generation_status:
                status_display.info(f"Status: {st.session_state.generation_status}")
            else:
                status_display.info("Ready to Generate Outline and Book")

            chapter_display.markdown(f"**Generating Chapter:** {st.session_state.current_chapter}")

            if st.session_state.process and st.session_state.process.poll() is None: # Check if process is running
                 with stop_button_col[0]: # Use the first column for button
                    if st.button("Stop Generation"):
                        if st.session_state.process:
                            os.killpg(os.getpgid(st.session_state.process.pid), signal.SIGTERM) # Send SIGTERM to the process group
                            st.session_state.stop_generation = True # Set stop flag
                            st.session_state.process = None # Reset process state
                            st.session_state.generation_status = "Generation Stopped by User"
                            status_display.warning("Generation Stopped by User")


            if st.session_state.generation_status == "Generating Book Content" and st.session_state.process:
                if st.session_state.process.poll() is not None: # Process finished
                    st.session_state.generation_status = "Book Generation Complete"
                    status_display.success("Book Generation Complete!")
                    chapter_display.empty() # Clear chapter display on completion
                    st.session_state.process = None # Reset process state
                    progress_bar.empty() # Clear progress bar
                    status_text_area.empty() # Clear status text area


    with tab3:
        st.header("Preview & Export")
        chapter_files_preview = glob.glob('book_output/chapter_*.txt')
        chapter_files_preview.sort()
        selected_chapter_file = st.selectbox("Select Chapter to Preview", chapter_files_preview)
        if selected_chapter_file:
            st.subheader(f"Preview of {selected_chapter_file}")
            preview_content = preview_chapter(selected_chapter_file)
            st.markdown(preview_content, unsafe_allow_html=True)
            st.session_state.preview_content = preview_content # Store preview content in session state

        st.subheader("Export Options")
        book_title_export = st.text_input("Book Title for Export", value=env_dict.get('BOOK_TITLE', 'My AI Book') + " export")
        book_author_export = st.text_input("Author Name for Export", value=env_dict.get('BOOK_AUTHOR', 'AI Author'))
        export_format = st.selectbox("Export Format", ["EPUB", "PDF"], index=0)
        chapters_dir = 'book_output'
        output_filename_base = f"{book_title_export.replace(' ', '_').lower()}_by_{book_author_export.replace(' ', '_').lower()}".replace(" ", "_")
        output_epub_path = os.path.join('book_output', f"{output_filename_base}.epub")
        output_pdf_path = os.path.join('book_output', f"{output_filename_base}.pdf")

        if st.button("Export Book"):
            if export_format == "EPUB":
                create_epub(book_title_export, book_author_export, chapters_dir, output_epub_path, cover_image_path)
                with open(output_epub_path, "rb") as epub_file:
                    st.download_button(
                        label="Download EPUB",
                        data=epub_file,
                        file_name=os.path.basename(output_epub_path),
                        mime="application/epub+zip"
                    )
                st.success(f"EPUB file created at: {output_epub_path}")

            elif export_format == "PDF":
                if export_to_pdf(output_epub_path, output_pdf_path): # Ensure EPUB exists before PDF conversion
                    with open(output_pdf_path, "rb") as pdf_file:
                        st.download_button(
                            label="Download PDF",
                            data=pdf_file,
                            file_name=os.path.basename(output_pdf_path),
                            mime="application/pdf"
                        )
                    st.success(f"PDF file created at: {output_pdf_path}")


def generate_book_process(api_key, progress_bar, status_text_area): # <-- DEFINED HERE NOW
    # Generation status and controls
    if not api_key:
        st.error("Please enter your API key")
        return

    # Generate book
    with st.spinner("Generating your book..."):
        try:
            process = subprocess.Popen(
                ['./quickstart.sh'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()

            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    status_text.text(output.strip())
                    if "Chapter" in output:
                        try:
                            chapter_num = int(output.split("Chapter")[1].split()[0])
                            progress = min(chapter_num / 10, 1.0)  # Assuming 10 chapters
                            progress_bar.progress(progress)
                        except:
                            pass

            if process.returncode == 0:
                st.success("Book generation completed!")
                st.session_state.generation_status = "completed"
            else:
                st.error("Book generation failed!")
                st.session_state.generation_status = "failed"
        except Exception as e:
            st.error(f"Error generating book: {str(e)}")
            st.session_state.generation_status = "failed"


if __name__ == "__main__":
    main()