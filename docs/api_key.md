# Testing API Keys

## OpenAI API Key

- Setup a virtual environment, install the dependencies, and activate the virtual environment using [Make](./dev_guide.md#using-the-makefile)
- Export your OpenAI API key

    ```bash
    export OPENAI_API_KEY="XXX"
    ```

- Run the script testing OpenAI API key

    ```bash
    python3 ./tests/apps/test_openai.py
    ```

- You will recieve a message indicating success or failure.
