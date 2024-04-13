# https://github.com/samuelcolvin/pydantic/blob/master/Makefile
export DOCKER_DEFAULT_PLATFORM=linux/amd64
.DEFAULT_GOAL := all

.PHONY: lint
lint:
	make -C api lint
	make -C parser lint

.PHONY: format
format:
	cd api && source .venv/bin/activate && make format && deactivate
	cd parser && source .venv/bin/activate && make format && deactivate

.PHONY: up
up:
	docker compose up -d --build --remove-orphans

.PHONY: up-api
up-api:
	docker compose up -d --build api database --remove-orphans

.PHONY: up-parsers
up-parsers:
	docker compose --profile parsers up -d

.PHONY: up-banki
up-banki:
	docker compose --profile banki up -d

.PHONY: up-sravni
up-sravni:
	docker compose --profile sravni up -d

.PHONY: up-vk
up-vk:
	docker compose --profile vk up -d

.PHONY: up-mdf
up-mdf:
	docker compose --profile mdf up -d

.PHONY: up-views
up-views:
	docker compose --profile views up -d

.PHONY: env
env:
	cp .env.example .env

.PHONY: all
all: format
