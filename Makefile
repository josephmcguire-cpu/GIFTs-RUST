SHELL=/bin/sh
VENV=.gifts

.PHONY: all build dev lint lint-fix test test-cov test-gifts test-validation test-demo test-e2e test-perf clean distclean

all: build

${VENV}:
	python3 -m venv ${VENV}
	${VENV}/bin/pip install --upgrade pip setuptools wheel

build: ${VENV}
	source ${VENV}/bin/activate; pip install build; python -m build

dev: ${VENV}
	source ${VENV}/bin/activate; pip install -e ".[test]"

lint: dev
	${VENV}/bin/ruff check conftest.py gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf tools/freeze_pipeline_cases.py
	${VENV}/bin/ruff format --check conftest.py gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf tools/freeze_pipeline_cases.py

lint-fix: dev
	${VENV}/bin/ruff check --fix conftest.py gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf tools/freeze_pipeline_cases.py
	${VENV}/bin/ruff format conftest.py gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf tools/freeze_pipeline_cases.py

# Per-area coverage gates match CI (see pyproject.toml / .github/workflows).
test: dev
	${VENV}/bin/pytest gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf -m "not perf" -q

# Combined coverage (gifts + validation/*.py + demo); htmlcov/index.html after run.
test-cov: dev
	${VENV}/bin/coverage erase
	${VENV}/bin/pytest gifts/tests validation/tests demo/tests tests/pipeline tests/e2e tests/perf -m "not perf" \
		--cov=gifts --cov=demo --cov=./validation \
		--cov-report=term-missing --cov-report=html

test-gifts: dev
	${VENV}/bin/coverage erase
	${VENV}/bin/pytest gifts/tests --cov=gifts --cov-report=term-missing --cov-fail-under=99

test-validation: dev
	${VENV}/bin/coverage erase
	${VENV}/bin/pytest validation/tests --cov=./validation --cov-report=term-missing --cov-fail-under=99

test-demo: dev
	${VENV}/bin/coverage erase
	${VENV}/bin/pytest demo/tests --cov=./demo --cov-report=term-missing --cov-fail-under=99

test-e2e: dev
	${VENV}/bin/pytest tests/e2e -m e2e -v

test-perf: dev
	${VENV}/bin/pytest tests/perf -m perf -v

clean: distclean
	rm -rf ${VENV}
	find . -name '*.py[co~]' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

distclean:
	find . -name '*.egg-info' -exec rm -rf {} +
	rm -rf .cache .eggs .pytest_cache build dist .coverage htmlcov .ruff_cache
