#!/bin/bash
# Скрипт для деплоя Telegram бота на сервер

set -e  # Прерывать скрипт при ошибках

# IP-адрес сервера
SERVER_IP="5.129.206.90"
SERVER_USER="root"
SERVER_PASSWORD="y8NSpBEVEy+zkP"

# Директория на сервере
REMOTE_DIR="/root/isreal-bot"

# Устанавливаем sshpass для автоматического ввода пароля
if ! command -v sshpass &> /dev/null; then
    echo "Установка sshpass..."
    if command -v brew &> /dev/null; then
        brew install sshpass
    else
        echo "Пожалуйста, установите sshpass вручную"
        exit 1
    fi
fi

# Создаем архив с файлами бота
echo "Создание архива с файлами бота..."
tar -czf bot_files.tar.gz bot.py requirements.txt Dockerfile docker-compose.yml

# Создаем директорию на сервере и копируем файлы
echo "Подключение к серверу и создание директории..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p ${REMOTE_DIR}"

# Копируем архив на сервер
echo "Копирование файлов на сервер..."
sshpass -p "${SERVER_PASSWORD}" scp -o StrictHostKeyChecking=no bot_files.tar.gz ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/

# Распаковываем архив на сервере и устанавливаем Docker 
echo "Распаковка файлов и установка Docker..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << EOF
    cd ${REMOTE_DIR}
    tar -xzf bot_files.tar.gz
    rm bot_files.tar.gz
    
    # Проверяем наличие Docker и устанавливаем при необходимости
    if ! command -v docker &> /dev/null; then
        echo "Установка Docker..."
        apt-get update
        apt-get install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
        add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable"
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io
    fi
    
    # Проверяем наличие Docker Compose и устанавливаем при необходимости
    if ! command -v docker-compose &> /dev/null; then
        echo "Установка Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    # Обновляем URL канала (при необходимости)
    sed -i 's|CHANNEL_URL = "https://t.me/yourchannelname"|CHANNEL_URL = "https://t.me/isreal_channel"|g' bot.py
    
    # Запускаем бота в Docker
    docker-compose up -d --build
    
    echo "Бот успешно запущен!"
EOF

# Удаляем локальный архив
rm bot_files.tar.gz

echo "Деплой успешно завершен!" 