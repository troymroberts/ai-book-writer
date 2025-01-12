"""O1-Preview configuration template"""

O1_PREVIEW_CONFIG = {
    "model": "o1-preview",
    "api_key": "",  # To be set by user
    "temperature": 0.7,
    "max_tokens": 1000,
    "stream": True,
    "timeout": 30,
    "request_timeout": 60,
    "max_retries": 3,
    "retry_min_wait": 1,
    "retry_max_wait": 10,
    "model_client_cls": "O1PreviewClient",
    "params": {
        "max_length": 2000,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    }
}
