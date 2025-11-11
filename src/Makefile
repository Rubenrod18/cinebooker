.PHONY: help run create_db migration migrate migrate-rollback seed test

# Alembic
ALEMBIC_CONFIG_FILE ?= app/migrations/alembic.ini
# Pytest
PARALLEL_TEST ?= auto
MAX_FAIL_TEST ?= 5


help:
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make COMMAND\033[36m\033[0m\n\n  A general utility script.\n\n  Provides commands to run the application, database migrations, tests, etc.\n  Next command start up the application:\n\n    \44 make run\n\nCommands:\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m \t%s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# =============================
# ==== DATABASE COMMANDS ======
# =============================
create_db:  ## Create the database of the application
	docker compose exec app uv run python cli.py create_db

migration:  ## Create a new migration based in new changes from database models
	docker compose exec app uv run alembic -c "${ALEMBIC_CONFIG_FILE}" revision --autogenerate -m '$(msg)'

migrate:  ## Upgrade to a later database migration
	docker compose exec app uv run alembic -c "${ALEMBIC_CONFIG_FILE}" upgrade head

migrate-rollback:  ## Revert to a previous database migration
	docker compose exec app uv run alembic -c "${ALEMBIC_CONFIG_FILE}" downgrade -1

seed:  ## Fill database with fake data
	docker compose exec app uv run python cli.py seed

# ==============================================
# ==== COVERAGE, LINTER AND TEST COMMANDS ======
# ==============================================
coverage: ## Report coverage statistics on modules
	coverage run -m pytest && coverage report -m

coverage-html: ## Create an HTML report of the coverage of the files
	coverage run -m pytest && coverage html

linter: ## Run Pylint on the app directory, disabling refactor warnings
	pylint . --disable=R --rcfile=.pylintrc

test: ## Run tests
	@uv run pytest

test-parallel:  ## Run tests in parallel
	@uv run pytest --numprocesses=$(PARALLEL_TEST) --maxfail=$(MAX_FAIL_TEST)
