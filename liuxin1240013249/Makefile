PYTHON ?= python3
SHELL := /bin/sh

.PHONY: all fetch reproduce validate check clean docker-build docker-run

all: reproduce validate

fetch:
	$(PYTHON) scripts/fetch_data.py

reproduce:
	$(PYTHON) scripts/run_triplicate.py

validate:
	$(PYTHON) scripts/validate_results.py

check: reproduce validate

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"

docker-build:
	docker build -t cs340-os-defects:1.0 .

docker-run:
	docker run --rm -v "$(PWD)/results:/work/results" cs340-os-defects:1.0
