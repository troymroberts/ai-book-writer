from typing import Dict, Optional, List
from string import Template
import json

class PromptConfig:
    """Configuration for prompt templates and variables"""
    
    def __init__(self, template: str, variables: Optional[Dict[str, str]] = None):
        """
        Initialize prompt configuration
        
        Args:
            template: The prompt template string
            variables: Dictionary of template variables and their values
        """
        self.template = template
        self.variables = variables or {}
        
    def render(self) -> str:
        """Render the prompt template with variables"""
        try:
            template = Template(self.template)
            return template.safe_substitute(self.variables)
        except Exception as e:
            raise ValueError(f"Failed to render prompt template: {str(e)}")
            
    def to_dict(self) -> Dict:
        """Convert prompt config to dictionary"""
        return {
            'template': self.template,
            'variables': self.variables
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'PromptConfig':
        """Create PromptConfig from dictionary"""
        if not isinstance(data, dict):
            raise ValueError("Prompt config must be a dictionary")
            
        if 'template' not in data:
            raise ValueError("Prompt config must specify a template")
            
        return cls(
            template=data['template'],
            variables=data.get('variables', {})
        )
        
    def validate(self) -> List[str]:
        """Validate the prompt configuration"""
        errors = []
        
        if not self.template.strip():
            errors.append("Prompt template cannot be empty")
            
        try:
            Template(self.template)
        except Exception as e:
            errors.append(f"Invalid template syntax: {str(e)}")
            
        return errors
