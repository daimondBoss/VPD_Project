@'
# Study Planner API

REST API для планирования подготовки к экзаменам: регистрация, вход по JWT, управление предметами.

**Стек:** FastAPI · SQLAlchemy 2.0 (sync) · PostgreSQL · Alembic · JWT (python-jose) · bcrypt

## Стек

| Слой | Технология |
|---|---|
| Web | FastAPI |
| ORM | SQLAlchemy 2.0 (sync) |
| БД | PostgreSQL 14+ |
| Миграции | Alembic |
| Аутентификация | JWT (HS256) + bcrypt |
| Конфиг | pydantic-settings + .env |

## Быстрый старт

### 1. Клонировать и подготовить окружение

    git clone https://github.com/daimondBoss/VPD_Project
    cd VPD_Project

    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate.ps1
    # Linux/macOS:
    source .venv/bin/activate

    pip install -r requirements.txt

### 2. Настроить .env

    copy .env.example .env

Откройте .env и укажите:

- DATABASE_URL — postgresql://postgres:ПАРОЛЬ@localhost:5432/VPD_Project
- SECRET_KEY — сгенерируйте:

    python -c "import secrets; print(secrets.token_urlsafe(64))"

### 3. Создать БД и применить миграции

    psql -U postgres -c "CREATE DATABASE \"VPD_Project\";"
    alembic upgrade head

### 4. Запуск

    uvicorn app.main:app --reload

- Swagger: http://127.0.0.1:8000/docs
- Healthcheck: http://127.0.0.1:8000/health

## API

### Auth — /auth

| Метод | Путь | Тело | Ответ |
|---|---|---|---|
| POST | /auth/register | email, password, name (опц.) | 201 + UserResponse |
| POST | /auth/login | email, password | 200 + access_token, token_type |

Пароль: 8–72 символа.
Дубликат email: 409 Conflict.

### Subjects — /subjects (Bearer-токен)

| Метод | Путь | Описание |
|---|---|---|
| GET | /subjects/ | Список своих предметов |
| POST | /subjects/ | Создать: title, color (опц.), exam_date |
| PATCH | /subjects/{id} | Изменить title / color / exam_date |
| DELETE | /subjects/{id} | Удалить (204) |

Аутентификация: Authorization: Bearer <access_token>.

Валидация:

- title — 1–100 символов
- exam_date — не раньше завтрашнего дня
- не больше 10 предметов на пользователя (400 при превышении)
- чужие предметы → 404

## Структура проекта

    VPD_Project/
    ├── app/
    │   ├── config.py         # Настройки из .env
    │   ├── database.py       # Движок + SessionDep
    │   ├── models.py         # SQLAlchemy-модели
    │   ├── schemas.py        # Pydantic-схемы
    │   ├── security.py       # bcrypt + JWT
    │   ├── dependencies.py   # get_current_user
    │   ├── main.py           # FastAPI + lifespan
    │   └── routers/
    │       ├── auth.py
    │       └── subjects.py
    ├── alembic/              # Миграции
    ├── .env.example
    ├── alembic.ini
    ├── requirements.txt
    └── README.md

## Правила разработки

- .env не коммитим — только .env.example. Секреты — в .env.
- Меняете модель — создаёте миграцию:

    alembic revision --autogenerate -m "краткое описание"
    alembic upgrade head

- Перед PR:

    alembic check   # No new upgrade operations detected

- Ветки: feature/<имя>, fix/<имя>. PR → main, ревью обязательно.
- Коммиты: feat:, fix:, chore:, docs:, refactor: (Conventional Commits).

## Roadmap

- [ ] CRUD для topics, exams
- [ ] Генерация учебного плана (study_plans, study_sessions)
- [ ] Настройки пользователя (/settings)
- [ ] Тесты (pytest + httpx2)
- [ ] CI (GitHub Actions)
'@ | Out-File README.md -Encoding UTF8

