# Synaptic Project Makefile

.PHONY: help start backend frontend install clean

# Default command
help:
	@echo "Available commands:"
	@echo "  make start      - Start both backend and frontend services in parallel"
	@echo "  make backend    - Start the FastAPI backend server (port 8000)"
	@echo "  make frontend   - Start the static UI server (port 8080)"
	@echo "  make install    - Install Python dependencies"
	@echo "  make clean      - Remove python cache files"

# Start both services
start:
	@echo "🚀 Starting Synaptic Services..."
	@make -j 2 backend frontend

# Backend service
backend:
	@echo "📡 Backend: http://localhost:8000"
	@uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend service
frontend:
	@echo "🎨 Frontend: http://localhost:8080"
	@python3 -m http.server 8080 --directory ui

# Dependencies
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
