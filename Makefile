all: inst format lint test

inst:
	poetry install --no-root

format:
	poetry run black ./app

lint:
	poetry run flake8 ./app
	poetry run pylint ./app

format-toml:
	poetry run toml-sort pyproject.toml --all --in-place



.PHONY: all inst lint format format-toml test
