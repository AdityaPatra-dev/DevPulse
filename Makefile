.PHONY: help build up down ps logs test clean

help:
	@echo "DevPulse Project Management Commands:"
	@echo "  make build   - Build multi-stage Docker image"
	@echo "  make up      - Launch complete Compose stack (App, DB, Nginx, Prometheus, Grafana, cAdvisor, node_exporter)"
	@echo "  make down    - Stop Compose stack (preserves volumes)"
	@echo "  make ps      - Check container status"
	@echo "  make logs    - View real-time container logs"
	@echo "  make test    - Run pytest test suite inside local container/environment"
	@echo "  make clean   - Stop stack and remove all named volumes (resets database)"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f

test:
	docker build -t devpulse-test --target builder .
	docker run --rm devpulse-test /bin/bash -c "pip install pytest httpx && pytest -v tests/"

clean:
	docker compose down -v
