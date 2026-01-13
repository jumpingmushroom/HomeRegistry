# HomeRegistry Makefile

.PHONY: help build up down logs clean backup restore dev

help:
	@echo "HomeRegistry - Available Commands:"
	@echo "  make build    - Build Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - View logs"
	@echo "  make clean    - Remove containers and volumes (WARNING: deletes data!)"
	@echo "  make backup   - Backup database and files"
	@echo "  make restore  - Restore from backup"
	@echo "  make dev      - Start in development mode"

build:
	@echo "Building Docker images..."
	docker-compose build

up:
	@echo "Starting HomeRegistry..."
	docker-compose up -d
	@echo "HomeRegistry is running at http://localhost:8080"

down:
	@echo "Stopping HomeRegistry..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "Cleaned up containers and volumes"; \
	fi

backup:
	@echo "Creating backup..."
	@mkdir -p backups
	docker run --rm -v homeregistry_homeregistry-data:/data -v $$(pwd)/backups:/backup \
		alpine tar czf /backup/homeregistry-backup-$$(date +%Y%m%d-%H%M%S).tar.gz /data
	@echo "Backup created in ./backups/"

restore:
	@echo "Available backups:"
	@ls -lh backups/
	@read -p "Enter backup filename: " backup; \
	docker run --rm -v homeregistry_homeregistry-data:/data -v $$(pwd)/backups:/backup \
		alpine sh -c "cd / && tar xzf /backup/$$backup"
	@echo "Restore complete"

dev:
	@echo "Starting in development mode..."
	@echo "Backend will be available at http://localhost:8000"
	@echo "Frontend will be available at http://localhost:5173"
	@echo ""
	@echo "Run these commands in separate terminals:"
	@echo "  Terminal 1: cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload"
	@echo "  Terminal 2: cd frontend && npm install && npm run dev"
