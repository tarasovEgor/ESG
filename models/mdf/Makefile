# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
.DEFAULT_GOAL := all
isort = isort app/ # tests/
black = black app/ # tests/
mypy = mypy app/
flake8  = flake8 app/ # tests/
pyupgrade = pyupgrade --py310-plus

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
	$(pyupgrade)
	$(isort)
	$(black)
	$(mypy)
	$(flake8)

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
	docker compose -f docker-compose.test.yaml up --build

.PHONY: migrate
migrate:
	cd app/database/ && ENV=migrate PYTHONPATH=../../ python3.10 -m alembic revision --autogenerate

.PHONY: downgrade
downgrade:
	cd app/database/ && ENV=migrate PYTHONPATH=../../ python3.10 -m alembic downgrade -1

.PHONY: upgrade
upgrade:
	cd app/database/ && ENV=migrate PYTHONPATH=../../ python3.10 -m alembic upgrade +1

.PHONY: upgrade-offline
upgrade-offline:
	cd app/database/ && ENV=migrate PYTHONPATH=../../ python3.10 -m alembic upgrade head --sql

.PHONY: all
all: format export-dependencies
