# Configuration Templates

This directory contains template configuration files for different LLM providers and genres. These templates can be copied and modified for specific use cases.

## LLM Provider Templates

- `openai.py`: Configuration template for OpenAI models
- `deepseek.py`: Configuration template for DeepSeek models
- `gemini.py`: Configuration template for Google Gemini models
- `groq.py`: Configuration template for Groq models
- `o1_preview.py`: Configuration template for O1-Preview models
- `gemini_flash.py`: Configuration template for Gemini Flash models

## Genre Templates

- `literary_fiction.py`: Template for literary fiction books
- `thriller_mystery.py`: Template for thriller/mystery books
- `fantasy_scifi.py`: Template for fantasy/science fiction books
- `romance.py`: Template for romance books
- `historical_fiction.py`: Template for historical fiction books
- `young_adult.py`: Template for young adult books
- `mysticism.py`: Template for mysticism/spirituality books
- `esoteric_philosophy.py`: Template for esoteric philosophy books
- `comparative_religion.py`: Template for comparative religion books
- `consciousness_studies.py`: Template for consciousness studies books
- `physics_textbook.py`: Template for physics textbooks
- `computer_science_textbook.py`: Template for computer science textbooks
- `engineering_textbook.py`: Template for engineering textbooks
- `mathematics_textbook.py`: Template for mathematics textbooks
- `chemistry_textbook.py`: Template for chemistry textbooks

## Using the Templates

1. **Copy the Template**
   ```bash
   cp config_templates/[template].py config.py
   ```
   Replace `[template]` with your chosen template

2. **Customize Settings**
   - Open `config.py`
   - Adjust any settings to fine-tune the generation
   - Each setting has detailed comments explaining its purpose

3. **Run the Generator**
   ```bash
   python main.py
   ```

## Notes

- Templates provide starting points - feel free to mix elements
- Consider your specific needs when adjusting settings
- Test different combinations to find the right balance
- Remember to backup your custom configurations
