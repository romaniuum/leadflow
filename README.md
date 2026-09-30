# leadflow

Мини-CRM для учета заявок: клиент, источник, сумма, статус по воронке.
Пет-проект, в разработке.

## Стек

Python 3.12, FastAPI, SQLAlchemy, PostgreSQL, Alembic, pytest,
Docker Compose, GitHub Actions, Terraform (Yandex Cloud), Prometheus + Grafana.

## Запуск

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
