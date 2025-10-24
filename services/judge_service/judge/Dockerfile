FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание рабочей директории
WORKDIR /app

# Копирование исходного кода
COPY app/ .

# Создание пользователя для безопасности
RUN useradd -m -u 1000 judge_user
USER judge_user

EXPOSE 8000

CMD ["python", "main.py"]