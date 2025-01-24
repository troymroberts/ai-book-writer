import litellm

litellm.set_verbose = True # Enable verbose logging for this test script

try:
    response = litellm.completion(
        model="ollama/deepseek-r1:14b",
        messages=[{"content": "Write a short test sentence.", "role": "user"}],
        base_url="http://localhost:11434"  # <--- Corrected base_url (no /api/v1/...)
    )
    print("\n--- Successful Response from Ollama ---")
    print(response)
    print("\nResponse Text:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n--- Error ---")
    print(f"Error connecting to Ollama: {e}")
    print("\nFull Exception Details:")
    import traceback
    traceback.print_exc()