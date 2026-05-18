# Health Tracker (Микросервисный бэкенд)

Микросервисный трекер здоровья на **FastAPI** с аутентификацией через JWT в **HttpOnly cookies**, контейнеризацией **Docker** и тестами **pytest**.

**Демо:** `https://your-app.up.railway.app/docs`

---

## 📦 Архитектура

| Сервис | Порт | Назначение |
|--------|------|-------------|
| **API Gateway** | 8001 | Единая точка входа, маршрутизация, JWT-аутентификация |
| **Auth Service** | 8000 | Регистрация, логин, добавление в базу данных|
| **App Service** | 8002 | Профиль пользователя, метрики (шаги/сон/вес/настроение), статистика |
| **PostgreSQL** | 5432 | База данных (отдельные БД для Auth и App сервисов) |

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/vladushkov11-lab/Health-Tracker.git
cd Health-Tracker
```
Скопируйте файл с примерами и отредактируйте его:

```bash
cp .env.example .env
```
2. В .env нужно указать реальные значения (пароли, ключи). Минимально необходимое:
```
SECRET_KEY=ваш_секретный_ключ
ALGORITHM=HS256

# PostgreSQL
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=db
DB_PORT=5432
DB_NAME=health_tracker
```
3. Запустить через Docker Compose

```bash
docker-compose up -d
```
После запуска будут доступны:

Swagger Gateway: http://localhost:8001/docs

Swagger Frontend: http://localhost:8003/docs

4. Остановить проект
```bash
docker-compose down
```
🧪 Тестирование

Проект покрыт тестами (pytest) которые поднимаются вместе с проектом 


📊 Возможности

Пользователи
Регистрация / логин
JWT в HttpOnly cookies

Обновление и удаление профиля

Метрики (ежедневные)
Шаги, калории, дистанция

Сон (часы, качество)

Вода, калории (приход)

Настроение (1–10), уровень стресса (1–10)

Статистика и аналитика
Графики (Chart.js)

Тренды (линейная регрессия)

BMI, BMR, рекомендации по активности

Автоматические инсайты (например: "Вы мало спали 3 дня подряд")

🛠 Технологии
```
Backend -	Python 3.11, FastAPI, Uvicorn.
Базы данных -	PostgreSQL, SQLAlchemy (async), Alembic
Аутентификация -	JWT, python-jose, bcrypt
Тестирование	Pytest, pytest-asyncio, httpx (mock)
Контейнеризация	Docker, Docker Compose
Фронтенд	Jinja2, Chart.js

