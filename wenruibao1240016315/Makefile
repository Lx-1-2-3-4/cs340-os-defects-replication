PY ?= python

.PHONY: all reproduce compare validate triplicate extension fig4d clean

all: reproduce compare validate

reproduce:
	$(PY) scripts/reproduce.py

compare:
	$(PY) scripts/compare.py

validate:
	$(PY) scripts/validate.py

triplicate:
	$(PY) scripts/triplicate.py

extension:
	$(PY) scripts/extension.py

fig4d:
	$(PY) scripts/fig4d_candidates.py

clean:
	rm -rf results/logs/run1 results/logs/run2 results/logs/run3
