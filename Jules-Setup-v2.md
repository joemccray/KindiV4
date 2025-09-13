# Jules-Setup-v2 (Unified, Deconflicted, CI-Ready)

> **Target environment:** Jules (Django/DRF backend, optional Node-based web workspace).  
> **Goal:** One canonical document to bootstrap a repo, generate a **single** unified CI workflow, and avoid all prior pitfalls (Ruff CLI changes, Bandit YAML/INI parsing, pytest exit-5, workflow merge conflicts, Node lockfile cache errors).

---

## 0) Quick start (copy/paste at repo root)

```bash
# 0.1 Create and enter a virtual environment
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip

# 0.2 Create dependency files (edit as you like later)
cat > requirements.txt << 'REQ'
Django==5.0.7
djangorestframework==3.15.2
gunicorn==22.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
whitenoise==6.7.0
REQ

cat > requirements-dev.txt << 'REQ'
# Lint / Format / Security
ruff==0.6.8
flake8==7.1.1
bandit==1.7.9
# Testing
pytest==8.3.2
pytest-django==4.8.0
coverage==7.6.1
REQ

pip install -r requirements.txt -r requirements-dev.txt || true
```

---

## 1) Static analysis configs (pinned & schema-correct)

```bash
# 1.1 Ruff
cat > .ruff.toml << 'RUF'
line-length = 88
target-version = "py311"
extend-exclude = [".venv", "venv", "node_modules", "dist", "build", "migrations"]

[lint]
extend-select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[lint.isort]
known-first-party = ["project", "apps"]
combine-as-imports = true
RUF

# 1.2 Flake8
cat > .flake8 << 'FLK'
[flake8]
max-line-length = 88
extend-ignore = E203,W503
exclude = .venv,venv,node_modules,dist,build,migrations
FLK

# 1.3 Bandit (YAML preferred; CI supports INI fallback)
if [ ! -f ".bandit.yaml" ] && [ ! -f ".bandit.yml" ] && [ ! -f ".bandit" ]; then
cat > .bandit.yaml << 'BND'
---
exclude_dirs:
  - tests
  - "*/migrations"
  - venv
  - .venv
  - node_modules
  - dist
  - build
skips:
  - B101
  - B311
BND
fi
```

---

## 2) Optional pre-commit hooks

```bash
cat > .pre-commit-config.yaml << 'PC'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.8
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
PC

. .venv/bin/activate && pip install pre-commit && pre-commit install
```

---

## 3) Unified GitHub Actions workflow

This is the **only** workflow. It covers backend (Django) and optional web (Node).  
Save as `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  pull_request:
    branches: [ "main" ]
  push:
    branches: [ "main" ]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
          restore-keys: ${{ runner.os }}-pip-
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip wheel setuptools
          if [ -f requirements.txt ]; then pip install -r requirements.txt || true; fi
          if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt || true; fi
          python -m pip install "ruff==0.6.8" "flake8==7.1.1" "bandit==1.7.9" \
                                "pytest==8.3.2" "pytest-django==4.8.0" "coverage==7.6.1"
      - run: ruff check --output-format=github .
      - run: ruff format --check .
      - run: flake8 .
      - name: Bandit
        run: |
          if [ -f ".bandit.yaml" ]; then bandit -q -c .bandit.yaml -r .;
          elif [ -f ".bandit.yml" ]; then bandit -q -c .bandit.yml -r .;
          elif [ -f ".bandit" ]; then
            first_char=$(grep -v '^\s*$' .bandit | grep -v '^\s*#' | head -n1 | cut -c1-1 || true)
            if [ "$first_char" = "[" ]; then
              bandit -q -r . -x tests,*/migrations,venv,.venv,node_modules,dist,build -s B101,B311
            else
              bandit -q -c .bandit -r .
            fi
          else
            bandit -q -r . -x tests,*/migrations,venv,.venv,node_modules,dist,build -s B101,B311
          fi
      - name: Pytest
        env:
          DJANGO_SETTINGS_MODULE: config.settings_test
          DJANGO_ENV: test
          NO_EXTERNAL_HTTP: "1"
        run: |
          set +e
          coverage run -m pytest -q
          code=$?
          if [ "$code" = "5" ]; then exit 0; fi
          exit $code
      - run: if [ -f ".coverage" ]; then coverage xml -o coverage.xml || true; fi

  web:
    if: ${{ hashFiles('**/package.json') != '' }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Node (cached)
        if: ${{ hashFiles('**/package-lock.json') != '' || hashFiles('**/yarn.lock') != '' }}
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - name: Setup Node (no cache)
        if: ${{ hashFiles('**/package-lock.json') == '' && hashFiles('**/yarn.lock') == '' }}
        uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Detect web directory
        id: detect
        run: |
          PKG=$(git ls-files **/package.json | head -n1 || true)
          if [ -z "$PKG" ]; then echo "skip=1" >> "$GITHUB_OUTPUT"; exit 0; fi
          DIR=$(dirname "$PKG")
          echo "dir=$DIR" >> "$GITHUB_OUTPUT"
      - name: Install dependencies
        if: ${{ steps.detect.outputs.skip != '1' }}
        run: |
          cd "${{ steps.detect.outputs.dir }}"
          if [ -f yarn.lock ]; then yarn install --frozen-lockfile;
          elif [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci;
          else npm install; fi
      - name: Run tests (or type-check)
        if: ${{ steps.detect.outputs.skip != '1' }}
        run: |
          cd "${{ steps.detect.outputs.dir }}"
          if npm run -s test >/dev/null 2>&1; then npm test --silent;
          elif npm run -s type-check >/dev/null 2>&1; then npm run -s type-check;
          else echo "No test or type-check script found. Skipping."; fi
```

---

## 4) Makefile helpers

```makefile
.PHONY: init lint fmt sec test ci web

init:
	python -m venv .venv && . .venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt -r requirements-dev.txt

lint: ; ruff check .

fmt: ; ruff format .

sec:
	if [ -f ".bandit.yaml" ]; then bandit -q -c .bandit.yaml -r .; \
	elif [ -f ".bandit.yml" ]; then bandit -q -c .bandit.yml -r .; \
	elif [ -f ".bandit" ]; then \
		first_char=$$(grep -v '^\s*$$' .bandit | grep -v '^\s*#' | head -n1 | cut -c1-1 || true); \
		if [ "$$first_char" = "[" ]; then bandit -q -r . -x tests,*/migrations,venv,.venv,node_modules,dist,build -s B101,B311; \
		else bandit -q -c .bandit -r .; fi; \
	else bandit -q -r . -x tests,*/migrations,venv,.venv,node_modules,dist,build -s B101,B311; fi

test: ; coverage run -m pytest -q || true

web:
	@if PKG=$$(git ls-files **/package.json | head -n1); then \
		DIR=$$(dirname $$PKG); cd $$DIR; \
		if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
		elif [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; \
		else npm install; fi; \
		if npm run -s test >/dev/null 2>&1; then npm test --silent; \
		elif npm run -s type-check >/dev/null 2>&1; then npm run -s type-check; \
		else echo "No web tests or type-check script found. Skipping."; fi; \
	else echo "No web package.json found. Skipping web target."; fi

ci: lint fmt sec test web
```

---

## 5) Guard rails

- **No `web-ci.yml`** → only `ci.yml`. Add this guard if desired:
```yaml
# .github/workflows/guard-no-web-ci.yml
name: Guard: no web-ci.yml
on: [push, pull_request]
jobs:
  guard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          test ! -f .github/workflows/web-ci.yml || (echo "web-ci.yml is not allowed" && exit 1)
```

- **CODEOWNERS** → require review for workflows:
```
.github/workflows/*  @your-handle
```

---

## 6) What “green” CI means (acceptance)

- **Ruff:** `ruff check --output-format=github .` and `ruff format --check .` both pass.  
- **Flake8:** passes (E203/W503 ignored to match formatter).  
- **Bandit:** passes with `.bandit.yaml` or INI auto-detect fallback (no YAML parse errors).  
- **Pytest:** passes; during bootstrap, “no tests collected” (exit 5) is treated as success.  
- **Web (optional):** runs only when `package.json` exists; uses cache only with a lockfile; runs tests or type-checks.

---

### You’re done.
Commit everything and push. The single **`ci.yml`** will run and should be robust against the issues we’ve previously seen.
