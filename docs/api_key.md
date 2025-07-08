# Testing API Keys

Setup a virtual environment, install the dependencies, and activate the virtual environment using [Make](./dev_guide.md#using-the-makefile)

## OpenAI API Key

- Export your OpenAI API environment variables

    ```bash
    export OPENAI_API_KEY="XXX"
    ```

- Run the script testing OpenAI API key

    ```bash
    python3 ./tests/apps/openai_api_key.py
    ```

- You will recieve a message indicating success or failure.

## Azure OpenAI API Key

- Export your Azure OpenAI API environment variables

    ```bash
    export AZURE_OPENAI_API_KEY="YOUR_API_KEY"
    export OPENAI_API_VERSION="2025-04-01-preview"
    export AZURE_OPENAI_ENDPOINT="https://YOUR_RESOURCE_NAME.openai.azure.com/"
    export AZURE_DEPLOYMENT_NAME="gpt-4o"

    ```

- Run the script testing Azure OpenAI API key

    ```bash
    python3 ./tests/apps/azure_openai_api_key.py
    ```

<!-- pyml disable line-length-->
- You will recieve a message indicating success or failure.
- See [Azure OpenAI Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?tabs=keyless%2Ctypescript-keyless%2Cpython-new%2Ccommand-line&pivots=programming-language-python) for more information.
<!-- pyml enable line-length-->

## Anthropic API Key

- Export your Anthropic API environment variables

    ```bash
    export ANTHROPIC_API_KEY="XXX"
    export ANTHROPIC_BASE_URL=https://api.anthropic.com/v1/
    export ANTHROPIC_MODEL_NAME=claude-3-sonnet-20240229
    ```

- Run the script testing OpenAI API key

    ```bash
    python3 ./tests/apps/anthropic_api_key.py
    ```

- You will recieve a message indicating success or failure.

## Gemini API Key

- Export your Gemini API environment variables

    ```bash
    export GOOGLE_API_KEY="XXX"
    export GOOGLE_MODEL_NAME=gemini-1.5-pro
    ```

- Run the script testing Gemini API key

    ```bash
    python3 ./tests/apps/gemini_api_key.py
    ```

- You will recieve a message indicating success or failure.
