# leadflow

[![CI](https://github.com/romaniuum/leadflow/actions/workflows/ci.yml/badge.svg)](https://github.com/romaniuum/leadflow/actions/workflows/ci.yml)

Мини-CRM для учета заявок: клиент, источник, сумма, статус по воронке.
Пет-проект, в разработке.

## Стек

Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Alembic, pytest,
Docker Compose, GitHub Actions, Terraform (Yandex Cloud), Prometheus + Grafana.

## Запуск в Docker

```bash
docker compose up -d --build
```

Поднимутся PostgreSQL и приложение, миграции применяются при старте.
API: http://localhost:8000, документация: http://localhost:8000/docs.
Остановить: `docker compose down` (данные остаются в volume `pgdata`,
удалить вместе с ними: `docker compose down -v`).

## Локальный запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Нужен PostgreSQL. Адрес берется из `DATABASE_URL`, по умолчанию
`postgresql+psycopg://leadflow:leadflow@localhost:5432/leadflow`.
Локально можно поднять так:

```bash
docker run -d --name leadflow-db -e POSTGRES_USER=leadflow \
  -e POSTGRES_PASSWORD=leadflow -e POSTGRES_DB=leadflow -p 5432:5432 postgres:17
```

Миграции и запуск:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API: http://localhost:8000, документация: http://localhost:8000/docs

## Тесты

Тесты используют отдельную базу из `TEST_DATABASE_URL`, по умолчанию
`leadflow_test` в том же контейнере. Таблицы создаются и удаляются автоматически.

```bash
docker exec leadflow-db psql -U leadflow -c "CREATE DATABASE leadflow_test"
pip install -r requirements-dev.txt
pytest
```

Линтер (то же самое запускается в CI):

```bash
ruff check .
ruff format --check .
```
