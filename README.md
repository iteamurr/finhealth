# FinHealth SMB

Анализатор финансового здоровья для продавцов на Wildberries и Ozon. Агрегирует продажи, комиссии, возвраты, логистику и рекламные расходы — и формирует P&L, ДДС, юнит-экономику по SKU и автоматические алерты на убыточные SKU, падение маржи и кассовые разрывы. MVP работает на тестовых данных без реальных API-запросов.

## Требования

- Docker
- Docker Compose v2

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd finhealth

# 2. Создать .env из шаблона
cp .env.example .env

# 3. Собрать и запустить стек (Postgres + API + Streamlit)
docker compose up -d --build

# 4. Применить миграции
docker compose exec app alembic upgrade head

# 5. Загрузить тестовые данные (20 SKU, 30 дней, возвраты, ДДС)
docker compose exec app python -m finhealth.infrastructure.seed.seed

# 6. Проверить API
curl -s localhost:8000/api/v1/health | python -m json.tool
```

- API: `http://localhost:8000` — документация по адресу `/docs`
- Дашборд: `http://localhost:8501`

## Пересев данных

Скрипт не идемпотентен при повторном запуске. Для полного пересева:

```bash
docker compose exec app alembic downgrade base
docker compose exec app alembic upgrade head
docker compose exec app python -m finhealth.infrastructure.seed.seed
```

Сид гарантирует: минимум 3 убыточных SKU и один кассовый разрыв > 7 дней для демонстрации алертов.

## Тесты

```bash
# Запустить все тесты
docker compose exec app pytest

# С покрытием доменного слоя
docker compose exec app pytest --cov=finhealth/domain tests/domain
```

---

## Бэкенд (FastAPI)

### Эндпоинты

Все маршруты под `/api/v1`. Даты принимаются в формате `YYYY-MM-DD`. Диапазон: `from_date <= to_date`, максимум 90 дней.

| Метод | Путь | Описание | Параметры |
|---|---|---|---|
| GET | `/api/v1/health` | Пинг БД; 503 если Postgres недоступен | — |
| GET | `/api/v1/dashboard` | Сводка: выручка, прибыль, кол-во алертов | `from_date`, `to_date` |
| GET | `/api/v1/pnl` | P&L с разбивкой по категориям затрат | `from_date`, `to_date`, `marketplace` (опц.: `WB` или `OZON`) |
| GET | `/api/v1/unit-economics` | Юнит-экономика по каждому SKU | `from_date`, `to_date` |
| GET | `/api/v1/cashflow` | ДДС с детекцией кассовых разрывов | `from_date`, `to_date` |
| GET | `/api/v1/alerts` | Алерты: убытки, низкая маржа, разрывы | `from_date`, `to_date` |

### Ошибки валидации

- `from_date > to_date` → HTTP 422 `{"detail": "from_date must be <= to_date"}`
- диапазон > 90 дней → HTTP 422 `{"detail": "Date range cannot exceed 90 days"}`

### Структура бэкенда

```
finhealth/
├── domain/           # Чистый Python: сущности, value objects, финансовый движок
├── use_cases/        # Один класс — один use case, оркестрирует DAO + домен
├── infrastructure/   # SQLAlchemy модели, DAO, сид
├── presentation/     # FastAPI роутеры, Pydantic схемы, DI
├── container.py      # DI-контейнер punq
└── main.py           # Фабрика FastAPI-приложения
```

**Стек:** FastAPI, SQLAlchemy 2.0 async, asyncpg, PostgreSQL 16, Alembic, Pydantic v2, punq, Faker, pytest.

---

## Фронтенд (Streamlit)

Дашборд для владельца бизнеса. Читает данные из FastAPI и отображает на пяти страницах.

### Страницы

- **Dashboard** — ключевые метрики, динамика прибыли, топ SKU
- **P&L** — стэковая диаграмма и таблица разбивки по затратам
- **Unit economics** — карточки SKU с водопадным графиком
- **Cash flow** — таймлайн выплат, предупреждения о разрывах
- **Alerts** — лента алертов по приоритету

### Запуск отдельно от Docker

Требование: бэкенд запущен на `http://localhost:8000`.

```bash
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/main.py
```

Открыть: `http://localhost:8501`.

### Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `API_BASE_URL` | `http://localhost:8000/api/v1` | Адрес FastAPI бэкенда |

Внутри Docker Compose `API_BASE_URL` автоматически устанавливается в `http://app:8000/api/v1`.

### Структура фронтенда

```
streamlit_app/
├── main.py         # точка входа, сайдбар, session state
├── config.py       # настройки и цветовая палитра
├── client/         # FinHealthClient на httpx (с кешированием)
├── components/     # metric_card, charts, alert_badge
└── pages/          # пять страниц Streamlit
```
