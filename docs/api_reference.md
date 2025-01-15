# API Reference

## LLM Integration

### Factory Interface
```python
class LLMFactory:
    def create_client(model_name: str) -> LLMClient:
        """
        Creates an LLM client instance
        
        Args:
            model_name: Name of the model to initialize
            
        Returns:
            Initialized LLMClient instance
        """
```

### Base Client
```python
class LLMClient:
    def generate_text(prompt: str, **kwargs) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input text prompt
            **kwargs: Model-specific parameters
            
        Returns:
            Generated text output
        """
```

## Template System

### Template Structure
```python
class BookTemplate:
    def __init__(self, genre: str, style: str):
        """
        Initialize book template
        
        Args:
            genre: Book genre (technical, fiction, etc.)
            style: Writing style (formal, casual, etc.)
        """
```

### Configuration
```python
class TemplateConfig:
    def load_template(template_name: str) -> BookTemplate:
        """
        Load template from config
        
        Args:
            template_name: Name of template to load
            
        Returns:
            Initialized BookTemplate instance
        """
```

## Error Handling

### Custom Exceptions
```python
class TemplateError(Exception):
    """Base template exception"""

class LLMConnectionError(Exception):
    """LLM connection failure"""
```

## Rate Limiting

```python
class RateLimiter:
    def check_limit() -> bool:
        """
        Check if rate limit is exceeded
        
        Returns:
            True if limit is not exceeded
        """
