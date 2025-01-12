"""Test connection to LLM services"""
import os
from llm.factory import LLMFactory

def main():
    """Test connection to LLM services"""
    # Get API key from environment
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("DEEPSEEK_API_KEY environment variable not set")
        return False
        
    # Test with DeepSeek configuration
    test_config = {
        'model': 'deepseek-chat',
        'api_key': api_key
    }
    
    try:
        # Create instance and attempt connection
        llm = LLMFactory.create_llm(test_config)
        
        # Try to make a simple API call
        result = llm.test_connection()
        
        if result:
            print("Connection test successful!")
        else:
            print("Connection test failed")
            
        return result
        
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

if __name__ == '__main__':
    main()
