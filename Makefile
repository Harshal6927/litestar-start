.PHONY: lint release

lint:
	@echo "Running linters... 🔄"
	pre-commit install
	pre-commit run -a
	ty check
	@echo "Linters completed. ✅"

release:
	@echo "Preparing release... 🔄"
	@python tools/prepare_release.py
	@uv sync
	@uv lock --upgrade
	@echo "Release prepared. ✅"
