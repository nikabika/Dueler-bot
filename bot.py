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
                btn_menu = types.InlineKeyboardButton("🗃️ Меню", callback_data="menu")
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
            try:
                if call.data == "search":
                    # Меняем сообщение на поиск
                    search_text = """*🔍 Поиск соперника....*
_Уже ищем тебе достойного соперника! Осталось только немного подождать..._"""
                    
                    markup = types.InlineKeyboardMarkup()
                    btn_cancel = types.InlineKeyboardButton("🙅‍♂️ Отмена", callback_data="cancel_search")
                    markup.add(btn_cancel)
                    
                    self.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=search_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    
                elif call.data == "menu":
                    # Меняем сообщение на меню
                    menu_text = """*🗃️ Меню*
_Выберите раздел из меню:_
• 🔍 Поиск соперника
• 👤 Профиль
• 🏆 Рейтинг
• ⚙️ Настройки
• ❓ Помощь"""
                    
                    markup = types.InlineKeyboardMarkup()
                    btn_back = types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_start")
                    markup.add(btn_back)
                    
                    self.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=menu_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    
                elif call.data == "cancel_search":
                    # Удаляем сообщение с поиском
                    self.bot.delete_message(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id
                    )
                    
                    # Отправляем новое сообщение об отмене
                    cancel_text = "🙅‍♂️ Поиск был отменен"
                    
                    markup = types.InlineKeyboardMarkup()
                    btn_search_again = types.InlineKeyboardButton("🔍 Искать снова", callback_data="search")
                    markup.add(btn_search_again)
                    
                    self.bot.send_message(
                        call.message.chat.id,
                        cancel_text,
                        parse_mode='Markdown',
                        reply_markup=markup
                    )
                    
                elif call.data == "back_to_start":
                    # Возвращаемся к начальному сообщению
                    name = call.from_user.first_name or "путешественник"
                    
                    welcome_text = f"""*🔥 Йоу, {name}!*
⚡ Вижу ты тут впервые. Что ж, это - игровой бот в телеграм для дуэлей между игроками, прямо здесь, в чате, оформленный в стиле Звездных Войн! Крутяк, да? В любом случае, давай уже начнем! 

_✨ А  если интересно, вот другие наши проекты:_
 - [ЧИБИКИ | Собирай коллекционных ребяток по вселенной далекой-далекой](https://t.me/chibeki_bot)
 - [Проекты | Наш тгк с новостями о ботах](https://t.me/tz_projects)

_Напиши /search чтобы найти соперника и /menu чтобы вызвать меню_"""
                    
                    markup = types.InlineKeyboardMarkup(row_width=2)
                    btn_search = types.InlineKeyboardButton("🔍 Поиск", callback_data="search")
                    btn_menu = types.InlineKeyboardButton("🗃️ Меню", callback_data="menu")
                    markup.add(btn_search, btn_menu)
                    
                    self.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=welcome_text,
                        parse_mode='Markdown',
                        reply_markup=markup,
                        disable_web_page_preview=True
                    )
                    
                # Отвечаем на callback query (убираем уведомление о загрузке)
                self.bot.answer_callback_query(call.id)
                
            except Exception as e:
                logger.error(f"Ошибка в обработке callback: {e}")
                try:
                    self.bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте снова")
                except:
                    pass

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
