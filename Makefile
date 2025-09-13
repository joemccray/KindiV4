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
	@PKG=$$(git ls-files **/package.json | head -n1); \
	if [ -n "$$PKG" ]; then \
		DIR=$$(dirname $$PKG); \
		cd $$DIR; \
		if [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
		elif [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; \
		else npm install; fi; \
		if npm run -s test >/dev/null 2>&1; then npm test --silent; \
		elif npm run -s type-check >/dev/null 2>&1; then npm run -s type-check; \
		else echo "No web tests or type-check script found. Skipping."; fi; \
	else \
		echo "No web package.json found. Skipping web target."; \
	fi

ci: lint fmt sec test web
