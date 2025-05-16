#!/bin/bash
# Скрипт для деплоя обновленного Telegram бота с базой данных

set -e  # Прерывать скрипт при ошибках

# IP-адрес сервера
SERVER_IP="5.129.206.90"
SERVER_USER="root"
SERVER_PASSWORD="y8NSpBEVEy+zkP"

# Директория на сервере
REMOTE_DIR="/root/isreal-bot"

# Создаем архив с файлами бота
echo "Подготовка файлов бота..."
cp bot_with_db.py bot.py

# Обновляем Dockerfile для поддержки базы данных
cat > Dockerfile << 'EOL'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .
RUN mkdir -p /app/data

VOLUME ["/app/data"]

CMD ["python", "bot.py"]
EOL

# Обновляем docker-compose.yml для поддержки базы данных
cat > docker-compose.yml << 'EOL'
version: '3'

services:
  bot:
    build: .
    restart: always
    volumes:
      - ./bot.py:/app/bot.py
      - ./data:/app/data
    environment:
      - DB_NAME=data/bot_users.db
EOL

echo "Создание архива с файлами бота..."
tar -czf bot_files.tar.gz bot.py Dockerfile docker-compose.yml

# Копируем архив на сервер
echo "Копирование файлов на сервер..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}/data"
sshpass -p "${SERVER_PASSWORD}" scp -o StrictHostKeyChecking=no bot_files.tar.gz ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/

# Распаковываем архив на сервере и перезапускаем бота
echo "Распаковка файлов и запуск бота..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << EOF
    cd ${REMOTE_DIR}
    tar -xzf bot_files.tar.gz
    rm bot_files.tar.gz
    
    # Останавливаем текущего бота и запускаем новую версию
    docker-compose down
    docker-compose up -d --build
    
    echo "Бот с поддержкой базы данных успешно запущен!"
EOF

# Удаляем временные файлы
rm bot.py Dockerfile docker-compose.yml bot_files.tar.gz

echo "Деплой успешно завершен!" 