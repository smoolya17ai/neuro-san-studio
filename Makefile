venv: ## Set up a virtual environment in project
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment in ./venv..."; \
		python3 -m venv venv; \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

install: venv ## Install all dependencies in the virtual environment
	@echo "Installing all dependencies including test dependencies in virtual environment..."
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt -r requirements-test.txt
	@echo "All dependencies including test dependencies installed successfully."

activate: ## Activate the venv
	@if [ ! -d "venv" ]; then \
		echo "No virtual environment detected..."; \
		echo "To create a virtual environment and install dependencies, run:"; \
		echo "    make install"; \
		echo ""; \
	else \
		echo "To activate the environment in your current shell, run:"; \
		echo "    source venv/bin/activate"; \
		echo ""; \
	fi

lint: ## Run code formatting and linting tools on source
	@if [ "$$(which python | grep -c "./venv")" -eq 0 ]; then \
		echo ""; \
		echo "Error: Linting must be run using the ./venv Python environment"; \
		echo "Please activate the correct environment with:"; \
		echo "  source venv/bin/activate"; \
		echo ""; \
		exit 1; \
	fi
	isort run.py coded_tools/ --atomic
	black run.py coded_tools/ --line-length 119
	flake8 run.py coded_tools/ --max-line-length 119 --extend-ignore W503,E203

lint-tests: ## Run code formatting and linting tools on tests
	@if [ "$$(which python | grep -c "./venv")" -eq 0 ]; then \
		echo ""; \
		echo "Error: Linting must be run using the ./venv Python environment"; \
		echo "Please activate the correct environment with:"; \
		echo "  source venv/bin/activate"; \
		echo ""; \
		exit 1; \
	fi
	isort tests/ --atomic
	black tests/ --line-length 119
	flake8 tests/ --max-line-length 119 --extend-ignore W503,E203

test: lint lint-tests ## Run tests with coverage
	python -m pytest tests/ -v --cov=coded_tools

.PHONY: help venv install activate lint lint-tests test
.DEFAULT_GOAL := help

help: ## Show this help message and exit
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'