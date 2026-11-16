PYTHON ?= python3

.PHONY: all test verify
all:
	"$(PYTHON)" -B scripts/run_all.py

test:
	"$(PYTHON)" -B -m unittest discover -s tests -v

verify:
	"$(PYTHON)" -B scripts/verify_results.py
