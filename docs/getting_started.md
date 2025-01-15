# Getting Started with AI Book Writer

This guide will help you quickly set up and start using the AI Book Writer.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- Node.js (for package management)
- Git (for version control)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ai-book-writer.git
   cd ai-book-writer
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r pinned_requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Set up environment variables:
   ```bash
   cp env.example .env
   ```
   Edit the .env file with your specific configuration values.

## Running the Application

To start the AI Book Writer:

```bash
python main.py
```

Or use the quickstart script:

```bash
./quickstart.sh
```

## First Steps

1. Select a genre or template from the available options
2. Configure your book settings
3. Generate your first book outline
4. Review and refine the generated content

## Troubleshooting

If you encounter any issues:
- Check the logs in the book_output directory
- Verify your .env configuration
- Ensure all dependencies are properly installed

For additional help, refer to the [Beginner's Guide](guides/beginners.md) or [Development Documentation](development/workflow.md).
