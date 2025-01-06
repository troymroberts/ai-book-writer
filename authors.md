# Writing Guide for Book Outlines

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
