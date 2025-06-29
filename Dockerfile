# syntax=docker/dockerfile:1
#
# Базовый Dockerfile для Telegram-бота Chains
#
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt ./

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Команда запуска бота (по умолчанию пустая, указать позже)
CMD ["python", "-m", "bot.main"] 