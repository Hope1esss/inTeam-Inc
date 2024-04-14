.PHONY: lint format-toml test install

install:
	poetry install --no-root
lint:
	poetry run flake8 ./app
	poetry run pylint ./app

format:
	poetry run black ./app

format-toml:
	poetry run toml-sort pyproject.toml --all --in-place

test:
	poetry run pytest