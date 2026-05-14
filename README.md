# FinHealth SMB

Financial health analyzer for sellers on Russian marketplaces (Wildberries, Ozon). Aggregates sales, commissions, returns, logistics costs, and ad spend to produce P&L, cash flow (ДДС), unit economics per SKU, and automated alerts for loss-making SKUs, margin drops, and cash gaps. MVP runs on mock seeded data only.

## Prerequisites

- Docker
- Docker Compose v2

## Quick start

```bash
# 1. Clone the repository
git clone <repo-url>
cd finhealth

# 2. Copy environment template
cp .env.example .env

# 3. Build and start the stack (Postgres + app)
docker compose up -d --build

# 4. Apply database migrations
docker compose exec app alembic upgrade head

# 5. Load seed data (20 SKUs, 30 days of orders, returns, cash flow)
docker compose exec app python -m finhealth.infrastructure.seed.seed

# 6. Verify the API is up
curl -s localhost:8000/api/v1/health | python -m json.tool
```

API docs are available at `http://localhost:8000/docs`.

## Running seed data separately

The seed script is idempotent for an empty database. To re-seed, drop and recreate the schema first.

```bash
# Re-seed (requires an empty schema)
docker compose exec app alembic downgrade base
docker compose exec app alembic upgrade head
docker compose exec app python -m finhealth.infrastructure.seed.seed
```

Seed output guarantees at least three loss-making SKUs and one cash gap > 7 days to demonstrate alerts.

## Endpoint reference

All endpoints live under `/api/v1`. Date query params accept `YYYY-MM-DD`. Date range is validated: `from_date <= to_date` and span <= 90 days.

| Method | Path | Description | Query params |
|---|---|---|---|
| GET | `/api/v1/health` | DB ping; returns 503 if Postgres is unreachable | none |
| GET | `/api/v1/dashboard` | Aggregated summary (revenue, profit, alerts count) | `from_date`, `to_date` |
| GET | `/api/v1/pnl` | Profit and loss breakdown, optionally filtered by marketplace | `from_date`, `to_date`, `marketplace` (optional: `WB` or `OZON`) |
| GET | `/api/v1/unit-economics` | Per-SKU revenue, costs, profit, margin, ROI | `from_date`, `to_date` |
| GET | `/api/v1/cashflow` | Daily cash flow timeline with gap detection | `from_date`, `to_date` |
| GET | `/api/v1/alerts` | Loss / low-margin / cash-gap alerts | `from_date`, `to_date` |

### Validation errors

- `from_date > to_date` -> HTTP 422 `{"detail": "from_date must be <= to_date"}`
- range > 90 days -> HTTP 422 `{"detail": "Date range cannot exceed 90 days"}`

## Running tests

```bash
# Inside the container
docker compose exec app pytest

# With coverage on the domain layer
docker compose exec app pytest --cov=finhealth/domain tests/domain
```

## Project layout

```
finhealth/
├── domain/           # Pure Python entities, value objects, financial engine
├── use_cases/        # One class per use case, orchestrates DAOs + domain
├── infrastructure/   # SQLAlchemy models, DAOs, seed data
├── presentation/     # FastAPI routers, Pydantic schemas, DI wiring
├── container.py      # punq DI container
└── main.py           # FastAPI app factory
```

## Stack

FastAPI, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16, Alembic, Pydantic v2, punq, Faker, pytest.
