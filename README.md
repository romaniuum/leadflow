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
uvicorn app.main:app --reload
```

API: http://localhost:8000, документация: http://localhost:8000/docs
