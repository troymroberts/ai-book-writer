# AutoGen Book Generator - Simple Guide

Welcome! Let's get you started with generating books using AI. Follow these easy steps:

## 1. Quick Setup

First, let's install what you need:

```bash
# 1. Get the code
git clone https://github.com/your-username/autogen-book-generator.git
cd autogen-book-generator

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt
```

## 2. Set Up Your API Key

You'll need an OpenAI API key:

1. Get your key from [OpenAI](https://platform.openai.com/api-keys)
2. Set it in your terminal:
```bash
export OPENAI_API_KEY="your-key-here"
```

## 3. Test Your Setup

Let's make sure everything works:
```bash
python -c "from llm.factory import LLMFactory; print(LLMFactory.test_connection())"
```

You should see `True` if everything is working!

## 4. Generate Your First Book

Now the fun part! Run:
```bash
python main.py
```

Follow the simple prompts to:
1. Choose a book type (fiction or non-fiction)
2. Pick a genre
3. Set how long you want it
4. Share your ideas

## Need Help?

If something doesn't work:
- Check your internet connection
- Make sure your API key is correct
- Try running the test again

That's it! You're ready to create amazing books with AI.

Happy writing!
