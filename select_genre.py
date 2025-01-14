#!/usr/bin/env python3
"""
Genre selection script for AI Book Writer
Displays all available genres and sets the selected genre in the environment
"""

import os
from typing import List, Dict, Tuple

def get_all_genres() -> List[Tuple[str, str]]:
    """Get all available genres with their template paths"""
    genres = []
    base_dir = "config_templates"
    
    # Get genres from genre directory
    genre_dir = os.path.join(base_dir, "genre")
    if os.path.exists(genre_dir):
        for file in os.listdir(genre_dir):
            if file.endswith(".py") and not file.startswith("__"):
                name = file[:-3].replace("_", " ").title()
                path = f"genre/{file[:-3]}"
                genres.append((name, path))
    
    # Get philosophy/religion templates from root directory
    philosophy_templates = [
        "comparative_religion",
        "consciousness_studies",
        "esoteric_philosophy",
        "mysticism"
    ]
    for template in philosophy_templates:
        if os.path.exists(os.path.join(base_dir, f"{template}.py")):
            name = template.replace("_", " ").title()
            path = template
            genres.append((name, path))
    
    # Get technical templates
    technical_dir = os.path.join(base_dir, "technical")
    if os.path.exists(technical_dir):
        for file in os.listdir(technical_dir):
            if file.endswith(".py") and not file.startswith("__") and "textbook" in file:
                name = file[:-3].replace("_", " ").title()
                path = f"technical/{file[:-3]}"
                genres.append((name, path))
    
    # Sort and group genres by category
    fiction = [(n, p) for n, p in genres if p.startswith("genre/")]
    philosophy = [(n, p) for n, p in genres if not p.startswith(("genre/", "technical/"))]
    technical = [(n, p) for n, p in genres if p.startswith("technical/")]
    
    # Return genres in category order
    return fiction + philosophy + technical

def display_genres(genres: List[Tuple[str, str]]) -> None:
    """Display all available genres in a formatted way"""
    import sys
    
    sys.stderr.write("\nAvailable Genres:\n")
    sys.stderr.write("-" * 50 + "\n")
    
    # Group genres by category
    fiction_genres = []
    philosophy_genres = []
    technical_genres = []
    
    for name, path in genres:
        if path.startswith("genre/"):
            fiction_genres.append((name, path))
        elif path.startswith("technical/"):
            technical_genres.append((name, path))
        else:
            philosophy_genres.append((name, path))
    
    # Display Fiction genres
    if fiction_genres:
        sys.stderr.write("\nFiction:\n")
        for i, (name, path) in enumerate(fiction_genres, 1):
            sys.stderr.write(f"{i:2d}. {name}\n")
    
    # Display Philosophy/Religion genres
    if philosophy_genres:
        sys.stderr.write("\nPhilosophy & Religion:\n")
        for i, (name, path) in enumerate(philosophy_genres, len(fiction_genres) + 1):
            sys.stderr.write(f"{i:2d}. {name}\n")
    
    # Display Technical genres
    if technical_genres:
        sys.stderr.write("\nTechnical:\n")
        for i, (name, path) in enumerate(technical_genres, len(fiction_genres) + len(philosophy_genres) + 1):
            sys.stderr.write(f"{i:2d}. {name}\n")

def select_genre() -> str:
    """Display genres and get user selection"""
    import sys
    
    genres = get_all_genres()
    while True:
        display_genres(genres)
        try:
            sys.stderr.write("\nEnter the number of your chosen genre: ")
            sys.stderr.flush()
            choice = input()
            index = int(choice) - 1
            if 0 <= index < len(genres):
                return genres[index][1]  # Return the genre path
            sys.stderr.write(f"Please enter a number between 1 and {len(genres)}\n")
        except ValueError:
            sys.stderr.write("Please enter a valid number\n")

def main():
    """Main function to handle genre selection"""
    import sys
    
    sys.stderr.write("Welcome to AI Book Writer Genre Selection\n")
    genre_path = select_genre()
    # Only print the genre path to stdout for shell script capture
    print(genre_path)

if __name__ == "__main__":
    main()
