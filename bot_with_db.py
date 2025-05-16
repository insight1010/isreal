import logging
import sqlite3
import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatMember
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from telegram.error import TelegramError

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота, полученный от BotFather
TOKEN = "7358724089:AAEN3tVjfM9e9kw61WOMgPtde0QILZ29dhU"

# URL и ID канала, на который нужно подписаться
CHANNEL_URL = "https://t.me/isreal_meta"
CHANNEL_ID = -1002602908716  # ВАЖНО: Используйте числовой ID канала без @. Получить можно через @userinfobot или API. Бот ДОЛЖЕН быть админом с правом просматривать участников!

# Имя файла базы данных
DB_NAME = "bot_users.db"

# ID администратора для отправки ошибок (замени на свой Telegram user_id)
ADMIN_ID = 123456789  # TODO: укажи свой user_id

# Инициализация базы данных
def init_db():
    """Создает таблицу пользователей, если она не существует"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        is_bot BOOLEAN,
        language_code TEXT,
        joined_date TEXT,
        last_active TEXT,
        is_subscribed BOOLEAN DEFAULT FALSE
    )
    ''')
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована")

# Проверка и добавление пользователя в базу данных
def add_or_update_user(user, is_subscribed=False):
    """Добавляет нового пользователя или обновляет существующего"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Проверяем, существует ли пользователь
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user.id,))
    existing_user = cursor.fetchone()
    
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if existing_user:
        # Обновляем данные существующего пользователя
        cursor.execute('''
        UPDATE users SET 
            username = ?,
            first_name = ?,
            last_name = ?,
            is_bot = ?,
            language_code = ?,
            last_active = ?,
            is_subscribed = ?
        WHERE user_id = ?
        ''', (
            user.username,
            user.first_name,
            user.last_name,
            user.is_bot,
            user.language_code,
            current_time,
            is_subscribed,
            user.id
        ))
        logger.info(f"Обновлена информация о пользователе: {user.id}")
    else:
        # Добавляем нового пользователя
        cursor.execute('''
        INSERT INTO users (
            user_id, username, first_name, last_name, 
            is_bot, language_code, joined_date, last_active, is_subscribed
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.is_bot,
            user.language_code,
            current_time,
            current_time,
            is_subscribed
        ))
        logger.info(f"Добавлен новый пользователь: {user.id}")
    
    conn.commit()
    conn.close()

# Проверка подписки пользователя на канал
async def check_subscription(context, user_id):
    """Проверяет, подписан ли пользователь на канал"""
    try:
        chat_member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        logger.info(f"Проверка подписки: user_id={user_id}, status={chat_member.status}")
        return chat_member.status in ["member", "administrator", "creator"]
    except TelegramError as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return None  # None если не удалось проверить

async def send_error_to_admin(context, error_text):
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"[BOT ERROR]\n{error_text}")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения админу: {e}")

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        is_subscribed = await check_subscription(context, user.id)
        add_or_update_user(user, is_subscribed)
        if is_subscribed:
            keyboard = [
                [InlineKeyboardButton("Перейти на канал", url=CHANNEL_URL)],
                [InlineKeyboardButton("Открыть интерфейс", url="https://insight1010.github.io/isreal/")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_html(
                f"Привет, это реально! 👋\n"
                f"Теперь ты в игре, где всё меняют инсайты.\n"
                f"Новости в канале подскажут, что делать дальше.\n\n"
                f"Поехали? 🚀",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Подписаться на канал", url=CHANNEL_URL)],
                [InlineKeyboardButton("✅ Я уже подписался", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_html(
                f"Привет, это реально! 👋\n"
                f"Для доступа к игре необходимо подписаться на наш канал.\n"
                f"После подписки нажмите кнопку «Я уже подписался».\n\n"
                f"Ждем тебя! 🚀",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")
        await send_error_to_admin(context, f"Ошибка в start: {e}")

# Обработчик кнопки "Я уже подписался"
async def button_callback(update: Update, context: CallbackContext) -> None:
    try:
        query = update.callback_query
        await query.answer()
        user = update.effective_user
        is_subscribed = await check_subscription(context, user.id)
        if is_subscribed is None:
            await query.edit_message_text(
                "Не удалось проверить подписку.\n\n"
                "Проверьте, что бот добавлен в канал @isreal_meta как администратор с правом просматривать участников!\n\n"
                "Если всё верно — попробуйте ещё раз через минуту."
            )
            return
        add_or_update_user(user, is_subscribed)
        if is_subscribed:
            keyboard = [
                [InlineKeyboardButton("Перейти на канал", url=CHANNEL_URL)],
                [InlineKeyboardButton("Открыть интерфейс", url="https://insight1010.github.io/isreal/")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Спасибо за подписку! 🎉\n"
                f"Теперь ты в игре, где всё меняют инсайты.\n"
                f"Новости в канале подскажут, что делать дальше.\n\n"
                f"Поехали? 🚀",
                reply_markup=reply_markup
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Подписаться на канал", url=CHANNEL_URL)],
                [InlineKeyboardButton("✅ Я уже подписался", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"Кажется, вы еще не подписались на наш канал.\n"
                f"Пожалуйста, подпишитесь на канал и затем нажмите кнопку «Я уже подписался».\n\n"
                f"Ждем вас! 🔍",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка в button_callback: {e}")
        await send_error_to_admin(context, f"Ошибка в button_callback: {e}")

# Обработчик для всех остальных сообщений
async def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        is_subscribed = await check_subscription(context, user.id)
        add_or_update_user(user, is_subscribed)
        if is_subscribed:
            await update.message.reply_text(
                "Чтобы начать сначала, используйте команду /start"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("Подписаться на канал", url=CHANNEL_URL)],
                [InlineKeyboardButton("✅ Я уже подписался", callback_data="check_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Для доступа к игре необходимо подписаться на наш канал.",
                reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")
        await send_error_to_admin(context, f"Ошибка в handle_message: {e}")

# Обработчик для получения статистики (админская команда)
async def get_stats(update: Update, context: CallbackContext) -> None:
    try:
        user = update.effective_user
        ADMIN_IDS = [ADMIN_ID]  # Используем ADMIN_ID
        if user.id not in ADMIN_IDS:
            await update.message.reply_text("У вас нет прав на выполнение этой команды.")
            return
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_subscribed = TRUE")
        subscribed_users = cursor.fetchone()[0]
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("SELECT COUNT(*) FROM users WHERE joined_date > ?", (yesterday,))
        new_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE last_active > ?", (yesterday,))
        active_users = cursor.fetchone()[0]
        conn.close()
        stats_message = (
            f"📊 Статистика бота:\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"✅ Подписанных на канал: {subscribed_users}\n"
            f"🆕 Новых за 24 часа: {new_users}\n"
            f"🔄 Активных за 24 часа: {active_users}"
        )
        await update.message.reply_text(stats_message)
    except Exception as e:
        logger.error(f"Ошибка в get_stats: {e}")
        await send_error_to_admin(context, f"Ошибка в get_stats: {e}")

def main() -> None:
    """Запускает бота."""
    # Инициализируем базу данных
    init_db()
    
    # Создаем приложение и передаем ему токен
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", get_stats))
    application.add_handler(CallbackQueryHandler(button_callback, pattern="check_subscription"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 