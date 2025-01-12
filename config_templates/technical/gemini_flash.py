"""Gemini Flash configuration template"""

GEMINI_FLASH_CONFIG = {
    "model": "gemini-flash",
    "api_key": "",  # To be set by user
    "temperature": 0.5,
    "max_tokens": 2048,
    "stream": True,
    "timeout": 30,
    "request_timeout": 60,
    "candidate_count": 1,
    "model_client_cls": "GeminiFlashClient",
    "safety_settings": {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
    },
    "params": {
        "max_output_tokens": 2048,
        "top_p": 0.95,
        "top_k": 40
    }
}
