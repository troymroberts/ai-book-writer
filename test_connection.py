from config import get_config, create_llm

def test_llm_connection():
    """Test connection to the LLM service"""
    try:
        # Get default configuration
        config = get_config()
        
        # Create LLM instance using first config
        llm = create_llm(config['config_list'][0])
        
        # Test with a simple prompt
        response = llm.generate("Test connection")
        
        if response:
            print("Connection successful! Response:", response)
            return True
        else:
            print("Connection failed - no response received")
            return False
            
    except Exception as e:
        print(f"Connection failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_llm_connection()
