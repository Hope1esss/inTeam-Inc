all: inst format lint format-toml

inst:
	poetry install --no-root

format:
	poetry run black ./app
	poetry run black ./alchemy_authentication_system

lint:
	poetry run flake8 ./app
	poetry run flake8 ./alchemy_authentication_system
	poetry run pylint ./app
	poetry run pylint ./alchemy_authentication_system

format-toml:
	poetry run toml-sort pyproject.toml --all --in-place

.PHONY: all inst lint format format-toml