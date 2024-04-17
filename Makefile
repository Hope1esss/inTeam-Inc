all: install format lint format-toml

install:
	poetry install --no-root

format:
	poetry run black ./app

lint:
	poetry run flake8 ./app
	poetry run pylint ./app

format-toml:
	poetry run toml-sort pyproject.toml --all --in-place

.PHONY: all install lint format format-toml