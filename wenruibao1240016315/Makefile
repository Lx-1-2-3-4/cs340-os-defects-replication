PY ?= python
MAIN ?= ../liuxin1240013249/results

.PHONY: all reproduce compare validate crosscheck triplicate extension fig4d layer layer-triplicate test clean

all: reproduce compare validate

reproduce:
	$(PY) scripts/reproduce.py

compare:
	$(PY) scripts/compare.py

validate:
	$(PY) scripts/validate.py

crosscheck:
	$(PY) scripts/crosscheck.py --main $(MAIN)

triplicate:
	$(PY) scripts/triplicate.py

extension:
	$(PY) scripts/extension.py

fig4d:
	$(PY) scripts/fig4d_candidates.py

layer:
	$(PY) scripts/layer_analysis.py

layer-triplicate:
	$(PY) scripts/run_layer_triplicate.py

test:
	$(PY) -m unittest discover -s tests

clean:
	rm -rf results/logs/run1 results/logs/run2 results/logs/run3
