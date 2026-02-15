.PHONY: lint release test

lint:
	@echo "Running linters... 🔄"
	ruff check --fix
	ty check
	pre-commit install
	pre-commit run -a
	@echo "Linters completed. ✅"

test:
	@echo "Running tests... 🔄"
	pytest tests
	@echo "Tests completed. ✅"

release:
	@echo "Preparing release... 🔄"
	@python tools/prepare_release.py
	@uv sync
	@uv lock --upgrade
	@echo "Release prepared. ✅"
