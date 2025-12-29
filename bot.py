import os
import telebot
from telebot import types
import logging
import time
import threading
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StarWarsBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.searchers = {}  # словарь ищущих игроков: {user_id: {'message_id': ..., 'search_start': ..., 'chat_id': ...}}
        self.lock = threading.Lock()
        self.setup_handlers()
        
        # Запускаем фоновую задачу для проверки таймаутов
        self.check_timeouts_thread = threading.Thread(target=self.check_search_timeouts, daemon=True)
        self.check_timeouts_thread.start()
        
        # Запускаем фоновую задачу для подбора матчей
        self.matchmaking_thread = threading.Thread(target=self.matchmaking_process, daemon=True)
        self.matchmaking_thread.start()
        
    def check_search_timeouts(self):
        """Проверка таймаутов поиска"""
        while True:
            time.sleep(1)  # Проверяем каждую секунду
            try:
                current_time = time.time()
                to_remove = []
                
                with self.lock:
                    for user_id, data in list(self.searchers.items()):
                        if current_time - data['search_start'] > 15:  # 15 секунд таймаут
                            # Меняем сообщение на предложение игры с ботом
                            try:
                                timeout_text = """*🔍 Поиск матча...*
_Так как поиск затянулся, ты можешь сыграть против бота! он не уступает людям ничем, кроме того, что не может общаться_"""
                                
                                markup = types.InlineKeyboardMarkup(row_width=2)
                                btn_fight = types.InlineKeyboardButton("✅ В бой!", callback_data="fight_bot")
                                btn_continue = types.InlineKeyboardButton("🙅‍♂️ Искать дальше", callback_data="continue_search")
                                markup.add(btn_fight, btn_continue)
                                
                                self.bot.edit_message_text(
                                    chat_id=data['chat_id'],
                                    message_id=data['message_id'],
                                    text=timeout_text,
                                    parse_mode='Markdown',
                                    reply_markup=markup
                                )
                                
                                # Обновляем данные в searchers
                                data['timeout_reached'] = True
                                data['timeout_time'] = current_time
                                
                            except Exception as e:
                                logger.error(f"Ошибка при обработке таймаута для {user_id}: {e}")
                                to_remove.append(user_id)
                    
                    # Удаляем неудачные попытки
                    for user_id in to_remove:
                        if user_id in self.searchers:
                            del self.searchers[user_id]
                            
            except Exception as e:
                logger.error(f"Ошибка в check_search_timeouts: {e}")
    
    def matchmaking_process(self):
        """Процесс подбора матчей"""
        while True:
            time.sleep(2)  # Проверяем каждые 2 секунды
            try:
                with self.lock:
                    # Берем только тех, кто ищет менее 15 секунд и не в режиме таймаута
                    active_searchers = [
                        (user_id, data) for user_id, data in self.searchers.items()
                        if not data.get('timeout_reached', False)
                    ]
                    
                    if len(active_searchers) >= 2:
                        # Выбираем случайную пару
                        player1_id, player1_data = random.choice(active_searchers)
                        # Ищем второго игрока, который не является первым
                        possible_opponents = [(uid, data) for uid, data in active_searchers if uid != player1_id]
                        
                        if possible_opponents:
                            player2_id, player2_data = random.choice(possible_opponents)
                            
                            # Создаем матч
                            match_id = f"{player1_id}_{player2_id}_{int(time.time())}"
                            
                            # Отправляем сообщения обоим игрокам
                            for user_id, user_data in [(player1_id, player1_data), (player2_id, player2_data)]:
                                opponent_id = player2_id if user_id == player1_id else player1_id
                                
                                match_text = f"""*🎮 Матч найден!*
_Соперник найден! Начинаем дуэль..._

🆔 ID матча: `{match_id}`
⚔️ Соперник: Игрок {opponent_id}"""
                                
                                self.bot.edit_message_text(
                                    chat_id=user_data['chat_id'],
                                    message_id=user_data['message_id'],
                                    text=match_text,
                                    parse_mode='Markdown'
                                )
                            
                            # Удаляем обоих из поиска
                            if player1_id in self.searchers:
                                del self.searchers[player1_id]
                            if player2_id in self.searchers:
                                del self.searchers[player2_id]
                                
            except Exception as e:
                logger.error(f"Ошибка в matchmaking_process: {e}")
    
    def start_search(self, chat_id, message_id, user_id, username=None):
        """Начинаем поиск матча (общая функция для /search и кнопки)"""
        try:
            # Добавляем пользователя в поиск
            with self.lock:
                self.searchers[user_id] = {
                    'message_id': message_id,
                    'search_start': time.time(),
                    'chat_id': chat_id,
                    'username': username,
                    'timeout_reached': False
                }
            
            # Меняем сообщение на поиск
            search_text = """*🔍 Поиск матча...*
_Уже ищем тебе достойного соперника! Осталось только немного подождать..._"""
            
            markup = types.InlineKeyboardMarkup()
            btn_cancel = types.InlineKeyboardButton("🙅‍♂️ Отмена", callback_data="cancel_search")
            markup.add(btn_cancel)
            
            self.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=search_text,
                parse_mode='Markdown',
                reply_markup=markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка в start_search: {e}")
            raise
        
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

        @self.bot.message_handler(commands=['search'])
        def handle_search(message):
            try:
                # Сначала отправляем сообщение о поиске
                search_text = """*🔍 Поиск матча...*
_Уже ищем тебе достойного соперника! Осталось только немного подождать..._"""
                
                markup = types.InlineKeyboardMarkup()
                btn_cancel = types.InlineKeyboardButton("🙅‍♂️ Отмена", callback_data="cancel_search")
                markup.add(btn_cancel)
                
                sent_msg = self.bot.send_message(
                    message.chat.id,
                    search_text,
                    parse_mode='Markdown',
                    reply_markup=markup
                )
                
                # Запускаем поиск
                self.start_search(
                    chat_id=message.chat.id,
                    message_id=sent_msg.message_id,
                    user_id=message.from_user.id,
                    username=message.from_user.username
                )
                
            except Exception as e:
                logger.error(f"Ошибка в /search: {e}")
                self.bot.send_message(message.chat.id, "Ошибка при начале поиска, попробуй позже.")

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            try:
                user_id = call.from_user.id
                
                if call.data == "search":
                    # Запускаем поиск из callback (та же функция что и для /search)
                    self.start_search(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        user_id=user_id,
                        username=call.from_user.username
                    )
                    
                elif call.data == "menu":
                    # Меняем сообщение на меню (пока заглушка)
                    menu_text = """*🗃️ Меню*
_Раздел в разработке... Скоро здесь появятся новые функции!_"""
                    
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
                    # Отменяем поиск
                    with self.lock:
                        if user_id in self.searchers:
                            del self.searchers[user_id]
                    
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
                    
                elif call.data == "continue_search":
                    # Продолжаем поиск после таймаута
                    with self.lock:
                        if user_id in self.searchers:
                            # Обновляем время начала поиска
                            self.searchers[user_id]['search_start'] = time.time()
                            self.searchers[user_id]['timeout_reached'] = False
                    
                    # Возвращаем к обычному поиску
                    self.start_search(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        user_id=user_id,
                        username=call.from_user.username
                    )
                    
                elif call.data == "fight_bot":
                    # Начинаем бой с ботом
                    with self.lock:
                        if user_id in self.searchers:
                            del self.searchers[user_id]
                    
                    bot_fight_text = """*🤖 Бой с ботом*
_Ты выбрал сражение с искусственным интеллектом! Готовься к битве..._

⚔️ Противник: ИИ-дроид MK-II
⭐ Сложность: Средняя
🎯 Шанс победы: 50%

_Бой начинается через 3... 2... 1..._"""
                    
                    self.bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=bot_fight_text,
                        parse_mode='Markdown'
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
