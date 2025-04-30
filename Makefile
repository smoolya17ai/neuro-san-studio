## Set up a virtual environment in backend
venv:
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment in ./venv..."; \
		python3 -m venv venv; \
		echo "Virtual environment created."; \
	else \
		echo "Virtual environment already exists."; \
	fi

## Install dependencies in the virtual environment
install: venv
	@echo "Installing all dependencies including test dependencies in virtual environment..."
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt -r requirements-test.txt
	@echo "All dependencies including test dependencies installed successfully."

## Activate the backend
activate:
	@echo "To activate the environment in your current shell, run:"
	@echo "    source venv/bin/activate"

## Run code formatting and linting tools on source
lint:
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

## Run code formatting and linting tools on tests
lint-tests:
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

## Run tests with coverage
test: lint lint-tests
	python -m pytest tests/ -v --cov=coded_tools