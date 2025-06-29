# Chains – Telegram-бот для крипто-игры (MVP)

## Описание
Chains — текстовый Telegram-бот, реализующий механику «цепочек» (Chains). Пользователь регистрируется по инвайт-ссылке, оплачивает участие (USDT TRC-20), получает персональную ссылку и приглашает ограниченное число игроков. После заполнения слотов продвигается по уровням, а на 10-м уровне может запустить собственную цепь.

## Возможности MVP
* Регистрация по инвайту и ввод USDT-кошелька.
* Выдача списка из 10 адресов для перевода и кнопки «Готово✅».
* Автоматическая проверка переводов через TronScan API.
* Генерация уникальной инвайт-ссылки c лимитом X = 3.
* Система слотов (⌛ ожидание / ✅ активен / ⚠️ просрочен / ❌ удалён).
* Команды:
  * `/start` — регистрация / получение ссылки.
  * `/status` — повторная проверка платежей.
  * `/myteam` — просмотр слотов и удаление неактивных.
* Фоновая задача: авто-экспирация слотов старше 24 ч.
* Хронологический changelog и task-tracker (в docs/).

## Быстрый старт (Docker-compose)
```bash
# 1. Клонируйте репозиторий и перейдите в каталог
# 2. Создайте .env на основе примера
cp .env.example .env  # и впишите BOT_TOKEN, TRONSCAN_API_KEY

# 3. Соберите и запустите контейнеры
docker compose up --build -d

# 4. Выполните миграцию схемы
docker compose exec bot alembic upgrade head
```

Бот автоматически начнёт polling Telegram API.

## Развёртывание без Docker
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="<token>"
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost/chains_db"
export TRONSCAN_API_KEY="<ключ>"

alembic upgrade head
python -m bot.main
```

## Структура проекта
```
bot/            исходники Telegram-бота
  handlers/     хэндлеры команд и callback-кнопок
  services/     работа с блокчейном, слотами, платежами
  middlewares/  DI-middleware (AsyncSession)
  config.py     централизованная загрузка настроек (.env)
db/             модели SQLAlchemy, миграции Alembic
docs/           changelog.md, tasktracker.md, project.md
```

## Переменные среды (.env)
| Переменная             | Описание                             |
|------------------------|--------------------------------------|
| `BOT_TOKEN`            | API-токен Telegram-бота              |
| `DATABASE_URL`         | строка подключения PostgreSQL        |
| `TRONSCAN_API_URL`     | URL TronScan API (по умолчанию prod) |
| `TRONSCAN_API_KEY`     | ключ TronScan PRO (необязательно)    |

## Тесты
Папка `tests/` подготовлена для pytest (пока пусто). Добавьте unit-тесты при расширении функционала.

## Roadmap
* Автоматическое создание новых уровней и цепей.
* Админ-панель (+REST API/Swagger).
* Интернационализация (RU/EN).
* Юнит-тесты и CI.

---
© 2025  Chains MVP 