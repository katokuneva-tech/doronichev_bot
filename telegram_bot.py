import os
import re
import time
import logging
import openai
import chromadb
from collections import defaultdict
from suggested_questions import get_random_questions
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import config
from analytics import BotAnalytics


load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

class DoronichevBot:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")

        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY не задан. Установи переменную окружения.")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN не задан. Установи переменную окружения.")

        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)

        self.chroma_client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
        self.collection = self.chroma_client.get_collection(config.COLLECTION_NAME)
        logger.info(f"База готова: {self.collection.count()} чанков")

        with open(config.SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()

        self.conversation_history = {}
        self._rate_limits = defaultdict(list)

        if config.ENABLE_ANALYTICS:
            self.analytics = BotAnalytics()

    def _is_rate_limited(self, user_id):
        """Проверка rate limit для пользователя."""
        now = time.time()
        timestamps = self._rate_limits[user_id]
        # Убираем старые записи
        self._rate_limits[user_id] = [t for t in timestamps if now - t < config.RATE_LIMIT_WINDOW]
        if len(self._rate_limits[user_id]) >= config.RATE_LIMIT_MESSAGES:
            return True
        self._rate_limits[user_id].append(now)
        return False
    
    def search_knowledge_base(self, query):
        try:
            response = self.openai_client.embeddings.create(
                input=query, 
                model=config.EMBEDDING_MODEL
            )
            results = self.collection.query(
                query_embeddings=[response.data[0].embedding], 
                n_results=config.N_RESULTS
            )
            return "\n\n".join(results["documents"][0])
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return ""
    
    def generate_response(self, user_message, context, user_id, first_name=None):
        try:
            history = self.conversation_history.get(user_id, [])

            messages = [{"role": "system", "content": self.system_prompt}]
            if context:
                messages.append({"role": "system", "content": f"Контекст: {context}"})
            if first_name:
                messages.append({"role": "system", "content": f"Имя собеседника: {first_name}"})

            for msg in history[-config.HISTORY_CONTEXT_MESSAGES:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            response = self.openai_client.chat.completions.create(
                model=config.MODEL,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )
            
            bot_response = response.choices[0].message.content
            
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].extend([
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": bot_response}
            ])
            
            if len(self.conversation_history[user_id]) > config.MAX_HISTORY_MESSAGES:
                self.conversation_history[user_id] = self.conversation_history[user_id][-config.MAX_HISTORY_MESSAGES:]
            
            return bot_response
        except Exception as e:
            logger.error(f"Ошибка генерации: {e}")
            return "Короче, что-то пошло не так. Попробуй еще раз."
    
    async def start_command(self, update, context):
        user_lang_code = update.effective_user.language_code or "ru"
        user_lang = "en" if user_lang_code.startswith("en") else "ru"
        
        text_ru = """Круто, ты здесь. 
Теперь дело за малым — задавай вопрос.
Хочешь про продукт? Стартап? Команду? Или мотивацию?
Я постараюсь объяснить так, как рассказал бы другу

🌍 Этот бот мультиязычный — можно общаться на любом языке.
🇺🇸 English | 🇷🇺 Русский | 🇪🇸 Español

Или вот одна из тем, которую можем разогнать:"""
        
        text_en = """Great to see you here!
Now the ball is in your court — ask away.
Want to discuss products? Startups? Teams? Or motivation?
I'll try to explain like I would to a friend

🌍 This bot is multilingual — feel free to ask in any language.
🇺🇸 English | 🇷🇺 Русский | 🇪🇸 Español 

Or here's one of the topics we can explore:"""
        
        text = text_ru if user_lang == "ru" else text_en
        
        # Получаем случайные вопросы (теперь это словари с teaser и full)
        questions = get_random_questions(user_lang, 3)
        
        # Сохраняем вопросы в контексте пользователя
        user_id = update.effective_user.id
        if not hasattr(context, 'user_data'):
            context.user_data = {}
        context.user_data['questions'] = questions
        
        # Создаем кнопки - показываем ТИЗЕРЫ
        keyboard = []
        for i, q in enumerate(questions):
            keyboard.append([InlineKeyboardButton(q["teaser"], callback_data=f"q_{i}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def help_command(self, update, context):
        text = """Я могу помочь с:
Продуктами — как запускать, находить инсайты, делать must-have  
Стартапами — от идеи до первых пользователей  
Мотивацией — как не сдаться, когда тяжело  
Командами — как собирать и вдохновлять людей  
Задавай вопрос и начнем."""
        await update.message.reply_text(text)
    
    async def feedback_command(self, update, context):
        text = """Есть вопросы или предложения? 
Пиши создателю бота: @kate_okunevaa

Буду рад любой обратной связи!"""
        await update.message.reply_text(text)
    
    async def clear_command(self, update, context):
        user_id = update.effective_user.id
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
        text = "✅ История диалога очищена. Начнём с чистого листа!"
        await update.message.reply_text(text)
    
    async def stats_command(self, update, context):
        user_id = update.effective_user.id
        
        if not config.ADMIN_USER_ID or user_id != config.ADMIN_USER_ID:
            await update.message.reply_text("Эта команда доступна только администратору.")
            return
        
        if not config.ENABLE_ANALYTICS:
            await update.message.reply_text("Аналитика отключена.")
            return
        
        stats = self.analytics.get_stats()
        
        text = f"""📊 Статистика бота:

👥 Всего пользователей: {stats['total_users']}
💬 Всего сообщений: {stats['total_messages']}
📅 Сообщений сегодня: {stats['messages_today']}
📈 Среднее сообщений на пользователя: {stats['avg_messages_per_user']}

🔥 Популярные темы:"""
        
        for keyword, count in stats['top_keywords']:
            text += f"\n  • {keyword}: {count}"
        
        await update.message.reply_text(text)
    
    def _is_forbidden_topic(self, text):
        """Проверка на запрещённые темы с учётом границ слов."""
        text_lower = text.lower()
        for word in config.FORBIDDEN_TOPICS:
            if re.search(rf'\b{re.escape(word)}\b', text_lower):
                return True
        return False

    async def handle_message(self, update, context):
        user_message = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or "без username"
        first_name = update.effective_user.first_name or ""

        if self._is_rate_limited(user_id):
            await update.message.reply_text("Подожди немного, слишком много сообщений подряд.")
            return

        # Отправляем уведомление админу
        admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        if admin_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=f"📨 Новый вопрос\n👤 @{username} (ID: {user_id})\n\n💬 {user_message}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки админу: {e}")

        if config.ENABLE_ANALYTICS:
            self.analytics.log_message(user_id, user_message)

        if self._is_forbidden_topic(user_message):
            await update.message.reply_text("Ну смотри, я больше про продукты и стартапы. Давай поговорим о чем-то полезном!")
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        context_info = self.search_knowledge_base(user_message)

        response = self.generate_response(user_message, context_info, user_id, first_name=first_name or None)

        # Отправляем ответ админу
        if admin_chat_id:
            try:
                await context.bot.send_message(
                    chat_id=admin_chat_id,
                    text=f"🤖 Ответ для @{username}:\n\n{response[:1000]}"
                )
            except Exception as e:
                logger.error(f"Ошибка отправки ответа админу: {e}")

        await update.message.reply_text(response)
    
    async def button_callback(self, update, context):
        """Обработка нажатий на кнопки с вопросами"""
        query = update.callback_query
        await query.answer()
    
        callback_data = query.data
    
        if not callback_data.startswith("q_"):
            return
    
        question_index = int(callback_data.split("_")[1])
    
        # Получаем вопрос из сохраненных данных
        if 'questions' not in context.user_data:
            await query.message.reply_text("Извините, вопросы устарели. Нажмите /start чтобы получить новые.")
            return
    
        questions = context.user_data['questions']
        if question_index >= len(questions):
            return
    
        # Берём ПОЛНЫЙ вопрос, а не тизер
        question = questions[question_index]["full"]

        user_id = query.from_user.id
        first_name = query.from_user.first_name or ""

        if config.ENABLE_ANALYTICS:
            self.analytics.log_message(user_id, question)

        await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")

        context_info = self.search_knowledge_base(question)

        response = self.generate_response(question, context_info, user_id, first_name=first_name or None)
        await query.message.reply_text(response)
    
    def run_bot(self):
        app = Application.builder().token(self.telegram_token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("feedback", self.feedback_command))
        app.add_handler(CommandHandler("clear", self.clear_command))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        app.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Бот запущен!")
        print(f"Модель: {config.MODEL}, Max tokens: {config.MAX_TOKENS}")
        app.run_polling()

if __name__ == "__main__":
    bot = DoronichevBot()
    bot.run_bot()
