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

## Инфраструктура

ВМ в Yandex Cloud описана в `terraform/`: сеть, подсеть, security group
(порты 22 и 8000) и ВМ на Ubuntu 24.04 с пользователем `deploy`.

Нужен сервисный аккаунт с ролью `editor` на каталог и его ключ в `terraform/key.json`:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars  # вписать cloud_id и folder_id
terraform init
terraform plan
terraform apply
```

После `apply` в выводе будет публичный IP и команда для SSH. Удалить все: `terraform destroy`.

## Деплой

На ВМ уже стоят Docker и git (ставятся через cloud-init). Деплой из ветки `main`:

```bash
./deploy.sh deploy@<ip>
```

При первом запуске скрипт склонирует репозиторий и попросит создать `.env`
на сервере (пример в `.env.example`), после этого запустить его еще раз.

## Мониторинг

Приложение отдает метрики Prometheus на `/metrics`. В compose вместе с приложением
поднимаются Prometheus и Grafana с готовым дашбордом leadflow
(запросы в секунду, задержки p50/p95, доля 5xx).

- Grafana: http://<ip>:3000, логин `admin`, пароль `GRAFANA_PASSWORD` из `.env`
  (локально `admin`)
- Prometheus наружу не открыт, только через SSH-туннель:
  `ssh -L 9090:localhost:9090 deploy@<ip>`, затем http://localhost:9090
