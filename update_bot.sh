#!/bin/bash
# Скрипт для обновления настроек Telegram бота на сервере

set -e  # Прерывать скрипт при ошибках

# IP-адрес сервера
SERVER_IP="5.129.206.90"
SERVER_USER="root"
SERVER_PASSWORD="y8NSpBEVEy+zkP"

# Директория на сервере
REMOTE_DIR="/root/isreal-bot"

# Создаем временный файл с обновленным ботом
cat > bot_updated.py << 'EOL'
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackContext

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота, полученный от BotFather
TOKEN = "7358724089:AAEN3tVjfM9e9kw61WOMgPtde0QILZ29dhU"

# URL канала, на который нужно дать ссылку
CHANNEL_URL = "https://t.me/isreal_meta"

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при получении команды /start."""
    user = update.effective_user
    
    # Создаем кнопку для перехода на канал
    keyboard = [
        [InlineKeyboardButton("Перейти на канал", url=CHANNEL_URL)],
        [InlineKeyboardButton("Открыть мини-приложение", url="https://insight1010.github.io/isreal/")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"Привет, это реально! 👋\n"
        f"Теперь ты в игре, где всё меняют инсайты.\n"
        f"Новости в канале подскажут, что делать дальше.\n\n"
        f"Поехали? 🚀",
        reply_markup=reply_markup
    )

def main() -> None:
    """Запускает бота."""
    # Создаем приложение и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
EOL

# Копируем обновленный файл на сервер
echo "Копирование обновленного файла на сервер..."
sshpass -p "${SERVER_PASSWORD}" scp -o StrictHostKeyChecking=no bot_updated.py ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/bot.py

# Перезапускаем бота на сервере
echo "Перезапуск бота на сервере..."
sshpass -p "${SERVER_PASSWORD}" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << EOF
    cd ${REMOTE_DIR}
    docker-compose restart
    echo "Бот успешно обновлен и перезапущен!"
EOF

# Удаляем временный файл
rm bot_updated.py

echo "Обновление успешно завершено!" 