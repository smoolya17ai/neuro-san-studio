# Development Guide

## Using the Makefile

This repository includes a Makefile with several useful commands to streamline development tasks.
**Note: These Makefile commands are designed for macOS and Unix-like systems and will not work directly on Windows.**

- `make venv` - Creates a virtual environment in the `./venv` directory if it doesn't already exist
- `make install` - Creates the virtual environment (if needed) and installs all dependencies including build dependencies
- `make activate` - Checks if the virtual environment exists and either provides activation instructions (if it exists)
or suggests running `make install` (if it doesn't)
- `make lint` - Runs code formatting and linting tools (isort, black, flake8) on the source code
- `make lint-tests` - Runs code formatting and linting tools on the test code
- `make test` - Runs lint and lint-tests, then executes the tests with pytest and generates coverage reports

These Makefile commands provide a convenient alternative to the manual steps described in the Installation section for
macOS users. Windows users should follow the manual installation instructions instead.

### Note on Markdown Linting

We use [markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) to run linting on .md files.
`markdownlint-cli` can be configured via `.markdownlint.yaml` located in the projects top level folder. See
this [yaml file](https://github.com/DavidAnson/markdownlint/blob/main/schema/.markdownlint.yaml) for all the configuration
options.

You can run `markdownlint-cli` in three ways:

- Using a Docker container

  - ```bash
    docker run -v ${PWD}:/workdir ghcr.io/igorshubovych/markdownlint-cli:latest "**/*.md" --ignore venv
    ```

  - The `-v` flag mounts a host directory into the container

- Using an installed version of `markdownlint-cli`
  - Install `markdownlint-cli` on your machine via [instructions](https://github.com/igorshubovych/markdownlint-cli?tab=readme-ov-file#installation)
  here

  - ```bash
    markdownlint -c .markdownlint.yaml "**/*.md" --ignore venv
    ```

  - The `-c` flag is used to pass in a configuration file to `markdownlint-cli`
  - To see all the options, run the following command:

    ```bash
    markdownlint --help
    ```

- If using VSCode IDE, using VSCode `markdownlint` extension

  - Install `markdownlint` extension by following these [instructions](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)

  - Any lines that violate one of markdownlint's rules will trigger a Warning in the editor. Warnings are indicated by a
  wavy green underline

`make lint` command invokes `markdownlint-cli` via an installed version of `markdownlint-cli`.

## Python Project Configuration

This project uses `pyproject.toml` for configuration of various Python development tools. This modern approach
centralizes tool configurations in a single file instead of using separate configuration files for each tool.

These configurations are automatically applied when running the relevant Makefile commands (`make lint`,
`make lint-tests`, `make test`).

## Contribution Workflow

This section outlines the recommended workflow for contributing to this project.

### Getting Started

1. **Fork the repository**: Create your own fork of the repository on GitHub.

2. **Clone your fork**:

   ```bash
   git clone https://github.com/your-username/neuro-san-studio.git
   cd neuro-san-studio
   ```

3. **Set up the development environment**:

   ```bash
   make install
   ```

   This will create a virtual environment and install all dependencies.

4. **Activate the virtual environment**:

   ```bash
   source venv/bin/activate  # On macOS/Linux
   ```

   Or follow the instructions provided by `make activate`.

### Making Changes

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature-name
   ```

   Use a descriptive name that reflects the changes you're making.

2. **Make your changes**: Implement your feature or fix.

3. **Follow code standards**:
   - Keep line length to 119 characters
   - Add docstrings to functions and classes
   - Include unit tests for new functionality

4. **Run linting and tests locally**:

   ```bash
   make lint      # Run linting on source code
   make lint-tests # Run linting on test code
   make test      # Run all tests and generate coverage reports
   ```

   Ensure all tests pass and there are no linting errors.

### Submitting Changes

1. **Commit your changes**:

   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

   Use clear and descriptive commit messages that explain what changes were made and why.

2. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Add a clear description of your changes
   - Reference any related issues

4. **Respond to feedback**: Be open to feedback and make requested changes if necessary.

### Keeping Your Fork Updated

To keep your fork up to date with the upstream repository:

```bash
# Add the upstream repository
git remote add upstream https://github.com/cognizant-ai-lab/neuro-san-studio.git

# Fetch changes from upstream
git fetch upstream

# Update your main branch
git checkout main
git merge upstream/main

# Update your feature branch (if needed)
git checkout feature/your-feature-name
git rebase main
```

Following this workflow will help ensure a smooth contribution process and maintain the project's quality standards.
