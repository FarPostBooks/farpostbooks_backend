# FarPostBooks - Backend
---
## API Endpoints:
- [x] `GET /users/token` - Получение токена, если пользователь зарегистрирован
- [x] `POST /users/{telegram_id}` - Создание нового пользователя
----
- [x] `GET /users/me` - Информация о себе _(scope: user)_
- [x] `GET /users/{telegram_id}` - Получение пользователя по telegram_id _(scope: user)_
- [x] `PUT /users/{telegram_id}` - Обновление данных пользователя _(scope: admin)_
---
- [x] `GET /books` - Список общего списка книг (ограничен по limit/offset) _(scope: admin)_
- [x] `GET /books/{book_id}` - Получение информации о книге по ISBN _(scope: admin)_
- [x] `POST /books/{book_id}` - Добавление новой книги по ISBN _(scope: admin)_
---
- [ ] `GET /users/{telegram_id}/books` - список всех книг юзера (ограниченный)
- [ ] `GET /users/{telegram_id}/books/{book_id}` - Получение подробной информации о книге пользователя по ISBN
- [ ] `PUT /users/{telegram_id}/books/{book_id}` - Обновление информации о книге пользователя (timestamp, rating)
- [ ] `POST /users/{telegram_id}/books/{book_id}` - Добавление новой книги

Список будет обновляться...

## Poetry

Для запуска проекта, используя poetry:
```bash
poetry install
poetry run python -m farpostbooks_backend
```

Проект будет запущен на хосте, указанном в `.env`.

Документация: `/api/docs`.\
Документация: `/api/redoc`.


## Docker

Запуск проекта, используя Docker:
```bash
docker-compose -f deploy/docker-compose.yml --project-directory . up --build
```

Запуск проекта для разработки в Docker с авто-перезагрузкой:
```bash
docker-compose -f deploy/docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up
```

При обновлении `poetry.lock` или `pyproject.toml` требуется пересобрать image с помощью команды:
```bash
docker-compose -f deploy/docker-compose.yml --project-directory . build
```

## Структура проекта

```bash
$ tree "farpostbooks_backend"
farpostbooks_backend
├── conftest.py  # Фикстуры для всех тестов.
├── db  # Конфигурация базы данных.
│   ├── dao  # Объекты доступа к данным. Содержит различные классы для взаимодействия с базой данных.
│   └── models  # Модели для Tortoise ORM.
├── __main__.py  # Запуск проекта, используя uvicorn.
├── services  # Взаимодействие со сторонними сервисами.
├── settings.py  # Основные параметры конфигурации проекта.
├── static  # Статика (документация).
├── tests  # Система тестирования.
└── web  # Веб-сервер. Обработчики, конфиг для запуска.
    ├── api  # Все хендлеры.
    │   └── router.py  # Главный роутер и подгрузка остальных.
    ├── application.py  # Конфигурация для FastAPI.
    └── lifetime.py  # Действия при запуске/остановке.
```

## Конфигурация
Все переменные окружения должны начинаться с префикса `FARPOSTBOOKS_BACKEND_`

Настройки переменных окружения находятся в `farpostbooks_backend.settings.Settings`.

## Pre-commit

Автоматическая проверка кода перед коммитом изменений. \
Конфигурация находится в `.pre-commit-config.yaml`.

Проверка кода происходит с использованием:
* black (форматирование кода);
* mypy (валидация тайп хинтинга);
* isort (сортировка импортов);
* flake8 (выявление возможных ошибок);


## Миграции


```bash
# Обновление БД до последней миграции (автоматически при запуске).
aerich upgrade
```

### Откат миграций

Для отката миграций используется команда:
```bash
aerich downgrade
```

### Генерация миграций

После обновления моделей требуется перегенерировать миграции командой:
```bash
aerich migrate
```


## Запуск тестов

Запуск тестов в докере с помощью команды:
```bash
docker-compose -f deploy/docker-compose.yml --project-directory . run --rm api pytest -vv .
docker-compose -f deploy/docker-compose.yml --project-directory . down
```
