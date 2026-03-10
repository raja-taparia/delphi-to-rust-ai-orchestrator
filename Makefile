PYTHON=python
PIP=pip

.PHONY: install test run clean

install:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test:
	@echo "Running tests..."
	$(PYTHON) -m unittest -q

run:
	@echo "Running orchestrator..."
	$(PYTHON) -m delphi_to_rust_ai_orchestrator

clean:
	@echo "Cleaning up..."
	rm -rf build/ dist/ *.egg-info/ __pycache__/ src/delphi_to_rust_ai_orchestrator/__pycache__/ tests/__pycache__/
