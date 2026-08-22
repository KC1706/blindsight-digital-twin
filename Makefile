.PHONY: install test demo clean

VENV := .venv
PY := $(VENV)/bin/python

install:  ## create venv + install deps
	python3 -m venv $(VENV)
	$(PY) -m pip install -q --upgrade pip
	$(PY) -m pip install -q -r requirements.txt

test:  ## run the test suite
	$(PY) -m pytest -q

demo:  ## run the ground-truth sim demo (SCENARIO=baseline|takt_slip_s14|torque_drift_s8|surge_3x)
	$(PY) -m engine.demo $(SCENARIO)

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__
