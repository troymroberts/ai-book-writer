import requests
import json

url = "http://localhost:11434/api/v1/generate" # <--- Construct the full URL based on documentation!

payload = {
    "model": "deepseek-r1:14b", # Or "deepseek-r1" - try both
    "prompt": "Write a short test sentence."
}
headers = {'Content-type': 'application/json'}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    print("\n--- Successful Response from Ollama (Direct API Call Test) ---")
    print(response.json()) # Or response.text if it's plain text
except requests.exceptions.RequestException as e:
    print("\n--- Error in Direct API Call Test ---")
    print(f"Error connecting to Ollama API endpoint: {e}")
    print("\nResponse status code:", response.status_code if 'response' in locals() else "No response")
    import traceback
    traceback.print_exc()