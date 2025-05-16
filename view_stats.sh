#!/bin/bash
# Скрипт для просмотра статистики пользователей в базе данных

SERVER_IP="5.129.206.90"
SERVER_USER="root"
SERVER_PASSWORD="y8NSpBEVEy+zkP"
REMOTE_DIR="/root/isreal-bot"

# Подключаемся к серверу и выполняем SQL-запрос к базе данных
echo "Получение статистики пользователей..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << EOF
    # Проверяем существование файла базы данных
    if [ -f "${REMOTE_DIR}/data/bot_users.db" ]; then
        echo "== Статистика пользователей =="
        echo ""
        
        # Общее количество пользователей
        TOTAL=\$(docker exec isreal-bot_bot_1 sqlite3 /app/data/bot_users.db "SELECT COUNT(*) FROM users")
        echo "Всего пользователей: \$TOTAL"
        
        # Новые пользователи за последние 24 часа
        YESTERDAY=\$(date -d "yesterday" +"%Y-%m-%d %H:%M:%S")
        NEW=\$(docker exec isreal-bot_bot_1 sqlite3 /app/data/bot_users.db "SELECT COUNT(*) FROM users WHERE joined_date > '\$YESTERDAY'")
        echo "Новых за 24 часа: \$NEW"
        
        # Активные пользователи за последние 24 часа
        ACTIVE=\$(docker exec isreal-bot_bot_1 sqlite3 /app/data/bot_users.db "SELECT COUNT(*) FROM users WHERE last_active > '\$YESTERDAY'")
        echo "Активных за 24 часа: \$ACTIVE"
        
        echo ""
        echo "== Последние 5 пользователей =="
        docker exec isreal-bot_bot_1 sqlite3 /app/data/bot_users.db "SELECT user_id, username, first_name, last_name, joined_date FROM users ORDER BY joined_date DESC LIMIT 5"
    else
        echo "База данных еще не создана или не содержит данных."
        echo "Взаимодействуйте с ботом, чтобы создать записи в базе данных."
    fi
EOF 