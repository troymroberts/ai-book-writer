import litellm
litellm.set_verbose = True  # Enable verbose logging for more detailed output

try:
    response = litellm.completion(
        model="ollama/deepseek-r1:14b",  # Full Ollama model string as model parameter
        messages=[{"content": "Write a short test sentence.", "role": "user"}],
        base_url="http://localhost:11434",
        provider="ollama"
    )
    print("\n--- Successful Response from Ollama (Direct Test - Variation 7) ---")
    print(response)
    print("\nResponse Text:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- Error in Direct Test (Variation 7) ---")
    print(f"Error connecting to Ollama directly: {e}")
    print("\nFull Exception Details:")
    import traceback
    traceback.print_exc()