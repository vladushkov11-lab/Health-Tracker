# Health Tracker (FastAPI + Docker)

Микросервисный бэкенд для трекера здоровья с авторизацией JWT (HttpOnly cookies), статистикой и тестами.

## Стек

- FastAPI (Gateway, Auth, App)
- PostgreSQL + SQLAlchemy (async)
- Docker / Docker Compose
- Pytest

## Быстрый старт

```bash
git clone https://github.com/vladushkov11-lab/health-tracker
cd health-tracker
cp .env.example .env
docker-compose up -d
