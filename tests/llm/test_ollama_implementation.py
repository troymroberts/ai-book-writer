import unittest
from unittest.mock import patch, MagicMock
from llm.litellm_implementations import OllamaImplementation
from types import SimpleNamespace

class TestOllamaImplementationCreate(unittest.TestCase):
    """Test cases for the OllamaImplementation.create function"""

    def setUp(self):
        """Set up test fixture"""
        self.model_name = "deepseek-r1:14b"
        self.base_url = "http://localhost:11434"
        self.ollama_impl = OllamaImplementation(model=self.model_name, ollama_base_url=self.base_url)
        self.sample_messages = [{"role": "user", "content": "Test message"}]
        self.sample_params = {"messages": self.sample_messages}

        # Patch litellm.completion to mock the API call
        self.litellm_completion_patcher = patch('llm.litellm_implementations.litellm.completion')
        self.mock_litellm_completion = self.litellm_completion_patcher.start()

        # Configure mock response for litellm.completion
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='Mocked response content'))]
        self.mock_litellm_completion.return_value = mock_response

    def tearDown(self):
        """Clean up test fixture"""
        self.litellm_completion_patcher.stop()

    def test_create_ollama_completion(self):
        """Test OllamaImplementation.create function"""
        result = self.ollama_impl.create(self.sample_params)

        # Assert that litellm.completion was called with the correct arguments
        self.mock_litellm_completion.assert_called_once_with(
            model=self.model_name, # Now passing just the model name
            messages=self.sample_messages,
            base_url=self.base_url,
            provider="ollama"
        )

        # Assert that the function returns a SimpleNamespace object
        self.assertIsInstance(result, SimpleNamespace)
        self.assertTrue(hasattr(result, 'choices'))
        self.assertTrue(hasattr(result, 'model'))

        # Assert that the response content is correctly extracted
        self.assertEqual(result.choices[0].message.content, 'Mocked response content')
        self.assertEqual(result.model, f"ollama/{self.model_name}") # Model name should be the full ollama model string


if __name__ == '__main__':
    unittest.main()