import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from flask import Flask, request

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))

if not TOKEN:
    logger.error("TOKEN environment variable is not set")
    raise ValueError("TOKEN environment variable is required")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name
    
    welcome_message = (
        f"*🔥 Йоу, {user_name}!*\n\n"
        f"⚡ Вижу ты тут впервые. Что ж, это - игровой бот в телеграм для дуэлей между игроками, "
        f"прямо здесь, в чате, оформленный в стиле Звездных Войн! Крутяк, да? В любом случае, давай уже начнем!\n\n"
        f"_✨ А если интересно, вот другие наши проекты:_\n"
        f" - [ЧИБИКИ | Собирай коллекционных ребяток по вселенной далекой-далекой](https://t.me/chibeki_bot)\n"
        f" - [Проекты | Наш тгк с новостями о ботах](https://t.me/tz_projects)\n\n"
        f"_Напиши /search чтобы найти соперника и /menu чтобы вызвать меню_"
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙️ Команда /search пока в разработке!")

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("⚙️ Команда /menu пока в разработке!")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_welcome(update, context)

application.add_handler(CommandHandler("start", start_command))
application.add_handler(CommandHandler("search", search_command))
application.add_handler(CommandHandler("menu", menu_command))

@app.post('/webhook')
async def webhook():
    json_data = await request.get_json()
    update = Update.de_json(json_data, application.bot)
    await application.process_update(update)
    return 'ok'

@app.get('/')
def index():
    return 'Бот работает! Отправьте /start в Telegram боту.'

async def setup_webhook():
    if WEBHOOK_URL:
        await application.bot.set_webhook(
            url=f"{WEBHOOK_URL}/webhook",
            drop_pending_updates=True
        )
        logger.info(f"Webhook установлен: {WEBHOOK_URL}/webhook")

def main() -> None:
    import asyncio
    
    asyncio.run(setup_webhook())
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    main()
