# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort .
black = black .
mypy = mypy .
flake8  = flake8 .
pyupgrade = pyupgrade --py310-plus
poetry = poetry run

.PHONY: install-linting
install-linting:
	poetry add flake8 black isort mypy pyupgrade -G dev

.PHONY: install
install: install-linting
	pre-commit install
	@echo 'installed development requirements'

.PHONY: lint
lint: install-linting
	$(isort) --df --check-only
	$(black) --diff --check
	$(flake8)

.PHONY: format
format:
	$(poetry) $(pyupgrade)
	$(poetry) $(isort)
	$(poetry) $(black)
	$(poetry) $(mypy)
	$(poetry) $(flake8)

.PHONY: export-dependencies
export-dependencies:
	poetry export -f requirements.txt --output requirements/requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements/requirements-dev.txt --without-hashes --with=dev
	poetry export -f requirements.txt --output requirements/requirements-test.txt --without-hashes --with=dev --with=test

.PHONY: database
database:
	docker run --name postgresql -e POSTGRES_USER=myusername -e POSTGRES_PASSWORD=mypassword -p 5432:5432 -d postgres

.PHONY: test
test:
	pytest --cov-report html --cov=.

.PHONY: env
env:
	cp .env.example .env

.PHONY: all
all: format export-dependencies
