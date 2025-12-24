import logging
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замени на свой)
TOKEN: Final = "8357197397:AAEiXz5uYjlnzIP6a1e79bLVh6mWrpecszI"

# Функция приветствия для новых пользователей
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение при старте бота."""
    
    # Получаем имя пользователя
    user_name = update.effective_user.first_name
    
    # Формируем приветственное сообщение с разметкой
    welcome_message = (
        f"*🔥 Йоу, {user_name}!*\n\n"
        f"⚡ Вижу ты тут впервые. Что ж, это - игровой бот в телеграм для дуэлей между игроками, "
        f"прямо здесь, в чате, оформленный в стиле Звездных Войн! Крутяк, да? В любом случае, давай уже начнем!\n\n"
        f"_✨ А если интересно, вот другие наши проекты:_\n"
        f" - [ЧИБИКИ | Собирай коллекционных ребяток по вселенной далекой-далекой](https://t.me/chibeki_bot)\n"
        f" - [Проекты | Наш тгк с новостями о ботах](https://t.me/tz_projects)\n\n"
        f"_Напиши /search чтобы найти соперника и /menu чтобы вызвать меню_"
    )
    
    # Отправляем сообщение с разметкой Markdown
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

# Заглушки для других команд (пока не реализованы)
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙️ Команда /search пока в разработке!")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙️ Команда /menu пока в разработке!")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await send_welcome(update, context)

def main() -> None:
    """Запуск бота."""
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("menu", menu_command))

    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
