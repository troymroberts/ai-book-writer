# Writing Guide for Book Outlines

## Story Settings Configuration

The book generator now includes powerful story settings that can be configured to shape your narrative. These settings are defined in `config.py` and can be adjusted to match your creative vision.

### Core Story Elements

1. **Character Settings**
   ```python
   CHARACTER_DEPTH = 0.8        # Higher values create more complex personalities
   CHARACTER_ARC_TYPE = "growth" # Options: "growth", "fall", "flat", "circular"
   CONFLICT_INTENSITY = 0.7     # Higher values increase dramatic tension
   EMOTIONAL_DEPTH = 0.8        # Higher values create deeper emotional resonance
   ```
   - Use high CHARACTER_DEPTH for complex protagonists
   - Choose CHARACTER_ARC_TYPE based on your story's needs:
     * "growth" - Character evolves positively
     * "fall" - Tragic or negative character development
     * "flat" - Character remains consistent
     * "circular" - Character returns to starting point
   - Adjust CONFLICT_INTENSITY based on genre (higher for thrillers, lower for slice-of-life)
   - Set EMOTIONAL_DEPTH higher for character-driven stories

2. **World Building Controls**
   ```python
   SETTING_DETAIL_LEVEL = 0.6   # Controls environmental description depth
   WORLD_COMPLEXITY = 0.7       # Affects world-building intricacy
   HISTORICAL_ACCURACY = 0.9    # For historical fiction accuracy
   ```
   - Increase SETTING_DETAIL_LEVEL for rich environmental descriptions
   - Higher WORLD_COMPLEXITY creates more detailed fictional worlds
   - Use high HISTORICAL_ACCURACY for period pieces

3. **Style and Structure**
   ```python
   NARRATIVE_STYLE = "third_person" # "first_person", "third_person", "omniscient"
   PACING_SPEED = 0.5              # Lower values create slower, detailed pace
   DIALOGUE_FREQUENCY = 0.6         # Balance between dialogue and narrative
   DESCRIPTIVE_DEPTH = 0.7          # Level of descriptive detail
   ```
   - Choose NARRATIVE_STYLE based on your storytelling preference
   - Adjust PACING_SPEED for different genres (lower for literary, higher for action)
   - Set DIALOGUE_FREQUENCY based on your scene needs
   - Use DESCRIPTIVE_DEPTH to control atmospheric detail

4. **Thematic Elements**
   ```python
   THEME_COMPLEXITY = 0.8    # Depth of thematic exploration
   SYMBOLIC_DENSITY = 0.6    # Frequency of symbolic elements
   MORAL_AMBIGUITY = 0.7    # Complexity of moral situations
   ```
   - Higher THEME_COMPLEXITY for literary fiction
   - Adjust SYMBOLIC_DENSITY for metaphorical richness
   - Use MORAL_AMBIGUITY to create complex ethical situations

### Recommended Settings by Genre

1. **Literary Fiction**
   ```python
   CHARACTER_DEPTH = 0.9
   EMOTIONAL_DEPTH = 0.9
   PACING_SPEED = 0.4
   THEME_COMPLEXITY = 0.9
   ```

2. **Thriller/Mystery**
   ```python
   CONFLICT_INTENSITY = 0.9
   PACING_SPEED = 0.8
   MORAL_AMBIGUITY = 0.8
   DIALOGUE_FREQUENCY = 0.7
   ```

3. **Fantasy/Sci-Fi**
   ```python
   WORLD_COMPLEXITY = 0.9
   SETTING_DETAIL_LEVEL = 0.8
   SYMBOLIC_DENSITY = 0.7
   DESCRIPTIVE_DEPTH = 0.8
   ```

### Using Settings with Outlines

When creating your outline, consider how these settings will interact with your chapter prompts. For example:

```
Chapter 1: The Awakening
--------------------------------------------------
[With high CHARACTER_DEPTH and EMOTIONAL_DEPTH]
Introduce the protagonist through their internal struggle,
showing complex layers of personality and deep emotional resonance.
Focus on psychological nuance and subtle character details.
```

### Tips for Effective Settings Use

1. **Balance Settings**: Avoid setting everything to maximum values
2. **Genre Alignment**: Match settings to your genre expectations
3. **Scene Variation**: Consider adjusting settings between chapters
4. **Testing**: Start with recommended presets and fine-tune based on results

This guide explains how to create custom book outlines using the `example_outline.txt` as a template. Follow these steps to create your own outline that can be used with the book generator.

## Outline Format

The outline should follow this structure:

```
Chapter 1: [Chapter Title]
--------------------------------------------------
[Detailed chapter prompt and instructions]

Chapter 2: [Chapter Title]
--------------------------------------------------
[Detailed chapter prompt and instructions]
```

## Creating Your Outline

1. **Chapter Titles**
   - Start each chapter with "Chapter X:" followed by the title
   - Titles should be descriptive and engaging
   - Example: `Chapter 1: The Discovery`

2. **Chapter Prompts**
   - After the chapter title, add a separator line (50 dashes)
   - Write detailed prompts that include:
     - Key plot points
     - Character development
     - Setting details
     - Tone and style guidance
   - Example:
     ```
     Introduce protagonist in their natural environment. Show their daily routine and hint at their internal conflict. The setting should be described in vivid detail, establishing the world and its rules.
     ```

3. **Chapter Length**
   - Each chapter prompt should be 3-5 paragraphs
   - Include enough detail to guide the writing but leave room for creativity
   - Example:
     ```
     Describe the protagonist's morning routine, emphasizing their meticulous nature. 
     Introduce the inciting incident - a mysterious letter arrives. 
     Show the protagonist's initial reaction and decision to investigate.
     ```

4. **Story Flow**
   - Ensure smooth transitions between chapters
   - Maintain consistent character voices and world rules
   - Build tension and stakes progressively

## Using Your Outline

1. Save your outline as `custom_outline.txt` in the project directory
2. Set the environment variable before running the generator:
   ```bash
   export CUSTOM_OUTLINE="book_output/custom_outline.txt"
   ```
3. Configure your LLM settings by exporting the required API keys:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export GOOGLE_API_KEY="your-google-key"  # For Gemini
   export GROQ_API_KEY="your-groq-key"
   export DEEPSEEK_API_KEY="your-deepseek-key"
   ```
   Note: Only export the keys for the LLM providers you plan to use.
4. Run the generator:
   ```bash
   python main.py
   ```

## Tips for Effective Outlines

- **Character Development**: Include notes about character arcs and motivations
- **World Building**: Add details about settings, rules, and atmosphere
- **Plot Structure**: Clearly mark key plot points and turning points
- **Pacing**: Indicate where to slow down or speed up the narrative
- **Themes**: Note any recurring themes or motifs to emphasize

## Example Outline Structure

Here's a sample structure based on `example_outline.txt`:

```
Chapter 1: The Discovery
--------------------------------------------------
Introduce protagonist in their laboratory. Describe their groundbreaking invention and the moment of discovery. Show their initial excitement and subsequent realization of the invention's potential consequences.

Chapter 2: The First Test
--------------------------------------------------
Detail the first field test of the invention. Include technical descriptions of the device in action. Show the protagonist's growing concern as unexpected results emerge.
```

Remember to save your outline as `custom_outline.txt` and set the environment variable before running the generator.
