import litellm

try:
    models = litellm.ollama_list_models()
    print("Ollama models listed successfully:")
    print(models)
except Exception as e:
    print(f"Error listing Ollama models from test script: {e}")
    print(f"Error details: {e}") # Added to print more error info