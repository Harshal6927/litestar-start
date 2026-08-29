.PHONY: lint release test

lint:
	@echo "Running linters... 🔄"
	uv run pre-commit install
	uv run pre-commit run -a
	@echo "Linters completed. ✅"

test:
	@echo "Running tests... 🔄"
	uv run pytest tests
	@echo "Tests completed. ✅"

release:
	@echo "Preparing release... 🔄"
	@uv run python tools/prepare_release.py
	@uv sync
	@uv lock --upgrade
	@echo "Release prepared. ✅"
