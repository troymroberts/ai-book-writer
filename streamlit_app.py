"""
Streamlit UI for AI Book Writer
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
from config.settings import Settings, LLMSettings
import logging
from logging.config import dictConfig
from agents import BookAgents
from book_generator import BookGenerator
from outline_generator import OutlineGenerator

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
        st.error("""Calibre is not installed. To enable PDF export, please install Calibre:
        
1. Using Homebrew:
   ```
   brew install --cask calibre
   ```
   
2. Or download from the official website:
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
        
        # Model selection
        available_models = [
            'deepseek-chat',
            'deepseek-reasoner',
            'openai/gpt-4',
            'openai/gpt-3.5-turbo',
            'gemini/gemini-pro',
            'groq/llama2-70b-4096'
        ]
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            index=available_models.index(env_dict.get('LLM__MODEL', 'deepseek-chat'))
        )
        
        # API configuration
        api_key = st.text_input(
            "API Key",
            value=env_dict.get('LLM__DEEPSEEK_API_KEY', ''),
            type="password"
        )
        
        # Genre selection
        genre_path = Path('config_templates/genre')
        if not genre_path.exists():
            st.error("Genre templates directory not found. Please check your installation.")
            return
            
        available_genres = [f.stem for f in genre_path.glob('*.py')]
        if not available_genres:
            st.error("No genre templates found. Please check your installation.")
            return
            
        current_genre = env_dict.get('BOOK_GENRE', '').replace('genre/', '')
        genre_index = available_genres.index(current_genre) if current_genre in available_genres else 0
        
        selected_genre = st.selectbox(
            "Select Genre",
            available_genres,
            index=genre_index
        )
        
        # Book metadata
        st.header("Book Metadata")
        book_title = st.text_input("Book Title", value="My AI Generated Book")
        author_name = st.text_input("Author Name", value="AI Author")
        
        # Optional cover image
        cover_image = st.file_uploader("Upload Cover Image (optional)", type=['jpg', 'jpeg', 'png'])
        
        # Generation parameters
        st.header("Generation Parameters")
        max_tokens = st.slider("Max Tokens", 1000, 8192, int(env_dict.get('GEN_MAX_TOKENS', '4096')))
        temperature = st.slider("Temperature", 0.0, 1.0, float(env_dict.get('GEN_TEMPERATURE', '0.7')))
        
        # Save configuration button
        if st.button("Save Configuration"):
            env_dict.update({
                'LLM__MODEL': selected_model,
                'LLM__DEEPSEEK_API_KEY': api_key,
                'BOOK_GENRE': f'genre/{selected_genre}',
                'GEN_MAX_TOKENS': str(max_tokens),
                'GEN_TEMPERATURE': str(temperature)
            })
            save_env_file(env_dict)
            st.success("Configuration saved!")
    
    with tab2:
        st.header("Book Generation")
        
        # Custom outline
        custom_outline = st.text_area(
            "Enter your custom outline (optional)",
            height=300,
            help="Enter your outline in markdown format with ### Chapter headers"
        )
        
        # Generation status and controls
        if st.button("Generate Book"):
            if not api_key:
                st.error("Please enter your API key")
                return
                
            # Save custom outline if provided
            if custom_outline:
                os.makedirs('book_output', exist_ok=True)
                with open('book_output/custom_outline.txt', 'w') as f:
                    f.write(custom_outline)
            
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
    
    with tab3:
        st.header("Preview & Export")
        
        # Chapter preview
        if os.path.exists('book_output'):
            chapter_files = sorted(glob.glob('book_output/chapter_*.txt'))
            if chapter_files:
                selected_chapter = st.selectbox(
                    "Select Chapter to Preview",
                    range(1, len(chapter_files) + 1),
                    format_func=lambda x: f"Chapter {x}"
                )
                
                chapter_path = f'book_output/chapter_{selected_chapter:02d}.txt'
                if os.path.exists(chapter_path):
                    st.markdown(preview_chapter(chapter_path), unsafe_allow_html=True)
                
                # Export options
                st.header("Export Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    # EPUB export
                    epub_path = os.path.join('book_output', f'{book_title.lower().replace(" ", "_")}.epub')
                    if st.button("Generate EPUB"):
                        try:
                            create_epub(book_title, author_name, 'book_output', epub_path,
                                     cover_image.name if cover_image else None)
                            st.success("EPUB generated successfully!")
                            
                            with open(epub_path, 'rb') as f:
                                st.download_button(
                                    label="Download EPUB",
                                    data=f,
                                    file_name=os.path.basename(epub_path),
                                    mime="application/epub+zip"
                                )
                        except Exception as e:
                            st.error(f"Error generating EPUB: {str(e)}")
                
                with col2:
                    # PDF export (requires Calibre)
                    if st.button("Generate PDF"):
                        if not check_calibre_installed():
                            st.error("""Calibre is required for PDF export. To install Calibre:
                            
1. Using Homebrew:
   ```
   brew install --cask calibre
   ```
   
2. Or download from the official website:
   https://calibre-ebook.com/download_osx""")
                        else:
                            pdf_path = os.path.join('book_output', f'{book_title.lower().replace(" ", "_")}.pdf')
                            if export_to_pdf(epub_path, pdf_path):
                                st.success("PDF generated successfully!")
                                with open(pdf_path, 'rb') as f:
                                    st.download_button(
                                        label="Download PDF",
                                        data=f,
                                        file_name=os.path.basename(pdf_path),
                                        mime="application/pdf"
                                    )
            else:
                st.info("No chapters generated yet. Generate your book first!")
        else:
            st.info("No book output found. Generate your book first!")

if __name__ == "__main__":
    main()
