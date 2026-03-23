SHELL=/bin/sh
VENV=.gifts

.PHONY: all build dev lint lint-fix test test-cov test-gifts test-validation test-demo test-e2e test-perf \
	docs docs-install docs-build docs-serve docs-dev docs-docker-build docs-clean clean distclean

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

# Docusaurus documentation site (docs-site/).
# Prefer: bash scripts/docs-with-npm.sh (NOT ./scripts/...) — see scripts/docs-with-npm.sh.
# Fallback with no local Node: make docs-docker-build  (requires Docker).
export NPM
DOCS_NPM = bash "$(CURDIR)/scripts/docs-with-npm.sh"

docs-install:
	$(DOCS_NPM) sh -ec 'cd "$(CURDIR)/docs-site" && if [ -f package-lock.json ]; then npm ci; else npm install; fi'

docs-build: docs-install
	$(DOCS_NPM) sh -ec 'cd "$(CURDIR)/docs-site" && npm run build'

# Preview the production build (run after docs-build, or use this target which builds first).
docs-serve: docs-build
	$(DOCS_NPM) sh -ec 'cd "$(CURDIR)/docs-site" && npm run serve'

# Live-reload dev server for editing docs (does not require a prior build).
docs-dev: docs-install
	$(DOCS_NPM) sh -ec 'cd "$(CURDIR)/docs-site" && npm start'

docs: docs-build

# Build static site using Node in Docker (no host npm required). Writes docs-site/node_modules + build via bind mount.
docs-docker-build:
	docker run --rm \
		-v "$(CURDIR)/docs-site:/app" \
		-w /app \
		node:20-bookworm-slim \
		sh -ec 'if [ -f package-lock.json ]; then npm ci; else npm install; fi && npm run build'

docs-clean:
	rm -rf docs-site/node_modules docs-site/build docs-site/.docusaurus

clean: distclean
	rm -rf ${VENV}
	find . -name '*.py[co~]' -exec rm -f {} +
	find . -type d -name '__pycache__' -exec rm -rf {} +

distclean:
	find . -name '*.egg-info' -exec rm -rf {} +
	rm -rf .cache .eggs .pytest_cache build dist .coverage htmlcov .ruff_cache \
		docs-site/build docs-site/.docusaurus
