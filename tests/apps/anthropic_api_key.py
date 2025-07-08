import os

from neuro_san.internals.run_context.langchain.util.api_key_error_check import ApiKeyErrorCheck
from openai import OpenAI


# Method for Testing Anthropic API key
#  Reads the Anthropic API keys from an environment variables,
#  Creates a client, and submits a simple query ("What's the capital of France?").
#  The response should includes the word "Paris".
#  Any exceptions (Invalid API Key, Azure OpenAI access being blocked, etc.) are reported.
def test_anthropic_api_key():

    # Set your Anthropic details
    api_key = os.getenv("ANTHROPIC_API_KEY")  # or use a string directly
    base_url = os.getenv("ANTHROPIC_BASE_URL")  # e.g., "https://api.anthropic.com/v1/"
    model_name = os.getenv("ANTHROPIC_MODEL_NAME")  # e.g., "claude-opus-4-20250514"

    # Create OpenAI client
    client = OpenAI(api_key=api_key, base_url=base_url)

    # Set up the client with your API key
    response = None
    try:

        # Make a chat completion request
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What's the capital of France?"},
            ],
        )

        # Print the assistant's reply
        print("Successful call to Anthropic")
        print(f"reponse: {response.choices[0].message.content}")

    except Exception as e:
        print("Failed call to Anthropic")
        print(f"Exception: {e}")
        exception_msg = ApiKeyErrorCheck.check_for_api_key_exception(e)
        print(f"Exception message: {exception_msg}")


if __name__ == "__main__":
    test_anthropic_api_key()
