# leadflow

[![CI](https://github.com/romaniuum/leadflow/actions/workflows/ci.yml/badge.svg)](https://github.com/romaniuum/leadflow/actions/workflows/ci.yml)

Мини-CRM для учета заявок. Заявка хранит клиента, источник, сумму и статус,
статус двигается по воронке `new → in_progress → won / lost`. По заявкам
считается конверсия и статистика по источникам.

Сделано на Python 3.12 и FastAPI с PostgreSQL, запускается в Docker Compose.
Инфраструктура в Yandex Cloud описана в Terraform, мониторинг на Prometheus и Grafana,
тесты и линтер гоняются в GitHub Actions.

## Как устроено

```mermaid
flowchart TB
    client(["Клиент"])
    dev(["Разработчик"])

    subgraph vm ["ВМ в Yandex Cloud, Docker Compose"]
        app["FastAPI :8000"] --> db[("PostgreSQL")]
        prometheus["Prometheus"] -->|"/metrics"| app
        grafana["Grafana :3000"] --> prometheus
    end

    client --> app
    dev --> grafana
    dev -->|"deploy.sh"| vm
    dev -->|"push"| github["GitHub"]
    github --> ci["GitHub Actions: ruff, pytest"]
    vm -->|"git pull"| github
    terraform["Terraform"] -->|"создает"| vm
```

Все сервисы работают в одном Docker Compose на ВМ. Наружу открыты только API
и Grafana, база и Prometheus доступны внутри сети Docker. ВМ создается Terraform,
код на нее попадает через `deploy.sh`: скрипт по SSH делает `git pull`
и пересобирает контейнеры.

## API

| Метод | Путь | Что делает |
|---|---|---|
| POST | `/leads` | создать заявку |
| GET | `/leads?status=new` | список заявок, фильтр по статусу необязательный |
| GET | `/leads/{id}` | одна заявка |
| PATCH | `/leads/{id}` | изменить клиента, источник или сумму |
| PATCH | `/leads/{id}/status` | сменить статус, недопустимый переход вернет 409 |
| DELETE | `/leads/{id}` | удалить заявку |
| GET | `/analytics/funnel` | заявки по статусам и конверсия |
| GET | `/analytics/sources` | заявки, выигранные сделки и конверсия по источникам |

Конверсия считается как `won / (won + lost)`, то есть только по закрытым заявкам.
Если закрытых нет, вернется `null`.

Полная документация в Swagger: `/docs`.

## Запуск

```bash
docker compose up -d --build
```

Поднимутся PostgreSQL, приложение, Prometheus и Grafana, миграции применяются при старте.

- API: http://localhost:8000/docs
- Grafana: http://localhost:3000 (`admin` / `admin`)
- Prometheus: http://localhost:9090

Остановить: `docker compose down`. Данные остаются в volumes,
удалить вместе с ними: `docker compose down -v`.

Пароли берутся из `.env` (пример в `.env.example`), без него используются
значения для локальной разработки.

## Разработка

Нужен Python 3.12 и PostgreSQL. Базу проще поднять отдельным контейнером:

```bash
docker run -d --name leadflow-db -e POSTGRES_USER=leadflow \
  -e POSTGRES_PASSWORD=leadflow -e POSTGRES_DB=leadflow -p 5432:5432 postgres:17
```

Через несколько секунд, когда база запустится, создать базу для тестов:

```bash
docker exec leadflow-db psql -U leadflow -c "CREATE DATABASE leadflow_test"
```

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Адрес базы берется из `DATABASE_URL`, по умолчанию
`postgresql+psycopg://leadflow:leadflow@localhost:5432/leadflow`.

Тесты работают с отдельной базой `leadflow_test` (`TEST_DATABASE_URL`),
таблицы создаются и удаляются автоматически. Перед push стоит прогнать то же, что и CI:

```bash
pytest
ruff check .
ruff format --check .
```

## Инфраструктура и деплой

В `terraform/` описаны сеть, подсеть, security group (порты 22, 8000 и 3000)
и ВМ на Ubuntu 24.04. При первом запуске cloud-init создает пользователя `deploy`
и ставит Docker.

Для Terraform нужен сервисный аккаунт с ролью `editor` на каталог
и его ключ в `terraform/key.json`:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars  # вписать cloud_id и folder_id
terraform init
terraform plan
terraform apply
```

После `apply` в выводе будет публичный IP. Деплой из ветки `main`:

```bash
./deploy.sh deploy@<ip>
```

Скрипт заходит на ВМ по SSH, обновляет код и перезапускает compose.
При первом запуске он склонирует репозиторий и остановится: на сервере нужно
создать `~/leadflow/.env` по образцу `.env.example` и запустить скрипт еще раз.

## Мониторинг

Приложение отдает метрики на `/metrics`. Prometheus собирает их раз в 15 секунд,
в Grafana есть дашборд leadflow: доступность, доля ошибок 5xx, запросы в секунду,
задержки p50/p95 и ответы по кодам.

На сервере Grafana открыта на порту 3000 (`admin`, пароль `GRAFANA_PASSWORD` из `.env`).
Prometheus без авторизации, поэтому наружу не открыт, только через SSH-туннель:

```bash
ssh -L 9090:localhost:9090 deploy@<ip>
```

Затем http://localhost:9090.
