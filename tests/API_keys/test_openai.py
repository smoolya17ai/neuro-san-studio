import os
from unittest import TestCase

from openai import OpenAI


class TestOpenAIAPIKey(TestCase):
    """
    Unit test for Testing OpenAI API key
    """

    def test_open_ai_api_key(self):
        """
        Test reads the OpenAI API key from an environment variable,
        creates a client, and submits a simple query ("What's the capital of France?").
        If the response includes "Paris", the tests passes. If not it will fail.
        Also, any exception (Invalid API Key, OpenAI access being blocked, etc.) causes the test to fail.
        """
        # Set up the client with your API key
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = None
        try:

            # Make a chat completion request
            response = client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What's the capital of France?"},
                ],
            )

            # Print the assistant's reply
            self.assertIn("Paris", response.choices[0].message.content, "'Paris' is not in the response")

        except Exception as e:
            self.fail(f"Exception type: {type(e).__name__}\nException message: {e}")
