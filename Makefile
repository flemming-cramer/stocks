.PHONY: audit
audit:
	python3 -m venv .venv || true
	. .venv/bin/activate && python -m pip install -U pip
	. .venv/bin/activate && pip install -q ruff vulture pycln deptry
	. .venv/bin/activate && python scripts/audit_unused_modules.py
	. .venv/bin/activate && ruff . --select F401,F841,ERA || true
	. .venv/bin/activate && vulture . --min-confidence 80 || true
	. .venv/bin/activate && deptry . || true
