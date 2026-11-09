PYTHON ?= python3
SHELL := /bin/sh

.PHONY: all fetch reproduce extension figure4-bootstrap validate check clean docker-build docker-run

all: reproduce validate extension

fetch:
	$(PYTHON) scripts/fetch_data.py

reproduce:
	$(PYTHON) scripts/run_triplicate.py

extension:
	$(PYTHON) extension/subsample_sensitivity.py --runs 3 --resamples 500
	$(PYTHON) extension/severity_missing_labels.py
	$(PYTHON) extension/figure4_bootstrap.py

figure4-bootstrap:
	$(PYTHON) extension/figure4_bootstrap.py

validate:
	$(PYTHON) scripts/validate_results.py

check: reproduce validate

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p) for p in pathlib.Path('.').rglob('__pycache__')]"

docker-build:
	docker build -t cs340-os-defects:1.0 .

docker-run:
	docker run --rm -v "$(PWD)/results:/work/results" cs340-os-defects:1.0
