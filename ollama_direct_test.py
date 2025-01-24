import litellm

try:
    response = litellm.completion(
        model="deepseek-r1:14b",  # Pass just the model name
        messages=[{"content": "Write a short test sentence.", "role": "user"}],
        base_url="http://localhost:11434",
        provider="ollama" # Explicitly set provider
    )
    print("\n--- Successful Response from Ollama (Direct Test) ---")
    print(response)
    print("\nResponse Text:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- Error in Direct Test ---")
    print(f"Error connecting to Ollama directly: {e}")
    print("\nFull Exception Details:")
    import traceback
    traceback.print_exc()