.PHONY: up down logs test lint format migrate seed clean smoke check-docs check-secrets

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	PYTHONPATH=.:backend pytest tests

lint:
	ruff check backend worker processor_adapter tests

format:
	ruff format backend worker processor_adapter tests

migrate:
	docker compose exec api alembic upgrade head

seed:
	./scripts/seed.sh

clean:
	docker compose down -v
	rm -rf data/studies/*
	touch data/studies/.gitkeep

smoke:
	./scripts/smoke.sh

check-docs:
	./scripts/check-docs.sh

check-secrets:
	./scripts/check-no-secrets.sh
