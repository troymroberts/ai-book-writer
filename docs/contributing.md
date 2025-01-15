# Contributing to AI Book Writer

We welcome contributions from the community! Please follow these guidelines when contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/decision-crafters/ai-book-writer.git
   cd ai-book-writer
   ```
3. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Coding Standards

- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Keep functions small and focused (max 50 lines)
- Write docstrings for all public methods
- Use descriptive variable names
- Format code with black (included in dev dependencies)

## Testing Requirements

- Write unit tests for all new functionality
- Maintain 90%+ test coverage
- Run tests before submitting PR:
  ```bash
  pytest --cov=ai_book_writer --cov-report=term-missing
  ```

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Describe your changes in the PR description:
   - What changes were made
   - Why they were made
   - Any relevant issue numbers
4. Request review from maintainers

## Code Review Guidelines

- Be constructive and professional
- Focus on code quality and maintainability
- Suggest improvements rather than just pointing out issues
- Respect the time and effort of contributors

## Reporting Issues

When reporting issues:
- Use the issue template
- Include steps to reproduce
- Provide expected vs actual behavior
- Include relevant logs or screenshots

## Style Guide

- Use double quotes for strings
- Use 4 spaces for indentation
- Keep lines under 120 characters
- Use snake_case for variables and functions
- Use PascalCase for class names

Thank you for contributing to AI Book Writer!
