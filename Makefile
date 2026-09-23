.PHONY: community-up up test lint open-core

community-up:
	git submodule update --init
	docker compose up --build community

up:
	git submodule update --init
	docker compose up --build

test:
	python3 -m pytest

lint:
	python3 -m ruff check overlay

open-core:
	bash scripts/check-open-core.sh
