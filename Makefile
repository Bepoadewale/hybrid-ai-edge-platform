PYTHON ?= python3
export PYTHONPATH := control-plane/src
test:
	$(PYTHON) -m pytest -q
