SHELL := /bin/bash # Use bash syntax
ARG := $(word 2, $(MAKECMDGOALS) )

clean:
	@find . -name "*.pyc" -exec rm -rf {} \;
	@find . -name "__pycache__" -delete

test:
	poetry run pytest backend/ $(ARG) --reuse-db

test_reset:
	poetry run pytest backend/ $(ARG)

backend_format:
	black backend

# Commands for Docker version
docker_setup:
	docker volume create query_cod_dbdata
	docker compose build --no-cache backend
	docker compose run --rm --remove-orphans backend python manage.py spectacular --color --file schema.yml
	docker compose run --remove-orphans frontend npm install
	docker compose run --rm --remove-orphans frontend npm run openapi-ts

docker_test:
	docker compose run --remove-orphans backend pytest $(ARG) --reuse-db

docker_test_reset:
	docker compose run --remove-orphans backend pytest $(ARG)

docker_up:
	docker compose up -d --remove-orphans

docker_update_dependencies:
	docker compose down
	docker compose up -d --build --remove-orphans

docker_down:
	docker compose down --remove-orphans

docker_logs:
	docker compose logs -f $(ARG)

docker_makemigrations:
	docker compose run --rm --remove-orphans backend python manage.py makemigrations

docker_migrate:
	docker compose run --rm --remove-orphans backend python manage.py migrate

docker_backend_shell:
	docker compose run --rm --remove-orphans backend bash

docker_backend_update_schema:
	docker compose run --rm --remove-orphans backend python manage.py spectacular --color --file schema.yml

docker_frontend_update_api:
	docker compose run --rm --remove-orphans frontend npm run openapi-ts
