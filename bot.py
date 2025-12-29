import os
import telebot
from telebot import types
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StarWarsBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.setup_handlers()
        
    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            try:
                name = message.from_user.first_name or "путешественник"
                
                welcome_text = f"""*🔥 Йоу, {name}!*
⚡ Вижу ты тут впервые. Что ж, это - игровой бот в телеграм для дуэлей между игроками, прямо здесь, в чате, оформленный в стиле Звездных Войн! Крутяк, да? В любом случае, давай уже начнем! 

_✨ А  если интересно, вот другие наши проекты:_
 - [ЧИБИКИ | Собирай коллекционных ребяток по вселенной далекой-далекой](https://t.me/chibeki_bot)
 - [Проекты | Наш тгк с новостями о ботах](https://t.me/tz_projects)

_Напиши /search чтобы найти соперника и /menu чтобы вызвать меню_"""
                
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn_search = types.InlineKeyboardButton("🔍 Поиск", callback_data="search")
                btn_menu = types.InlineKeyboardButton("📋 Меню", callback_data="menu")
                markup.add(btn_search, btn_menu)
                
                self.bot.send_message(
                    message.chat.id,
                    welcome_text,
                    parse_mode='Markdown',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
                
            except Exception as e:
                logger.error(f"Ошибка в start: {e}")
                self.bot.send_message(message.chat.id, "Ошибка соединения, попробуй позже.")

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            if call.data == "search":
                self.bot.answer_callback_query(call.id, "Поиск соперника...")
                self.bot.send_message(
                    call.message.chat.id,
                    "⚙️ Поиск пока в разработке!",
                    parse_mode='Markdown'
                )
            elif call.data == "menu":
                self.bot.answer_callback_query(call.id, "Меню...")
                self.bot.send_message(
                    call.message.chat.id,
                    "⚙️ Меню пока в разработке!",
                    parse_mode='Markdown'
                )

    def run(self):
        logger.info("Star Wars Bot запущен!")
        self.bot.infinity_polling()


if __name__ == "__main__":
    TOKEN = os.environ.get('TOKEN')
    
    if not TOKEN:
        logger.error("TOKEN environment variable is not set")
        raise ValueError("TOKEN environment variable is required")
    
    bot = StarWarsBot(TOKEN)
    bot.run()
