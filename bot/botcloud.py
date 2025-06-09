# bot/bot.py - Главный файл бота (упрощенный)
"""
Основной файл бота - только инициализация и регистрация
"""

import os
import logging
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler

# Загружаем переменные окружения
load_dotenv()

# Импортируем обработчики
from .handlers.claude import handle_claude, handle_claude_callback
from .handlers.deepseek import handle_deepseek, handle_deepseek_callback
from .handlers.dashka import handle_dashka, handle_dashka_callback
from handlers.voice import VoiceHandler
from core.orchestrator import Orchestrator

# Инициализация
orchestrator = Orchestrator(providers)
voice_handler = VoiceHandler(orchestrator)

# Регистрация обработчика
@dp.message_handler(content_types=types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    text_response = await voice_handler.handle_voice(message)
    
    # Отправляем текстовый ответ
    await message.reply(text_response)
    
    # Опционально: отправляем голосовой ответ
    voice_path = await voice_handler.generate_voice_response(text_response)
    await message.reply_voice(types.InputFile(voice_path))
    os.unlink(voice_path)


# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AISolarBot:
    """Главный класс бота"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        self.application = ApplicationBuilder().token(self.token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Регистрация всех обработчиков"""
        
        # Команды AI провайдеров
        self.application.add_handler(CommandHandler("claude", handle_claude))
        self.application.add_handler(CommandHandler("deepseek", handle_deepseek))
        self.application.add_handler(CommandHandler("dashka", handle_dashka))
        
        # Callback обработчики для inline кнопок
        self.application.add_handler(CallbackQueryHandler(
            handle_claude_callback, 
            pattern="^claude_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            handle_deepseek_callback, 
            pattern="^deepseek_"
        ))
        self.application.add_handler(CallbackQueryHandler(
            handle_dashka_callback, 
            pattern="^dashka_"
        ))
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(CommandHandler("help", self._handle_help))
        self.application.add_handler(CommandHandler("status", self._handle_status))
        
        logger.info("✅ Все обработчики зарегистрированы")
    
    async def _handle_start(self, update, context):
        """Команда /start"""
        welcome_text = """🤖 **AI Solar 2.0** - Многопровайдерный AI ассистент

**Доступные AI:**
🧠 `/claude` - Архитектурный анализ и планирование
🔍 `/deepseek` - Программирование и алгоритмы  
⚙️ `/dashka` - Техподдержка и диагностика

**Пример использования:**
`/claude Как спроектировать микросервисную архитектуру?`

Выберите подходящий AI для вашей задачи! ✨"""
        
        await update.message.reply_markdown_v2(self._escape_markdown(welcome_text))
    
    async def _handle_help(self, update, context):
        """Команда /help"""
        help_text = """📚 **Справка AI Solar 2.0**

**Команды:**
• `/start` - Начать работу
• `/help` - Эта справка
• `/status` - Статус AI провайдеров

**AI Провайдеры:**

🧠 **Claude** (`/claude вопрос`)
• Архитектурный анализ
• Планирование систем
• Сравнение технологий
• Оценка решений

🔍 **DeepSeek** (`/deepseek задача`)
• Программирование
• Алгоритмы и структуры данных
• Code review
• Оптимизация кода

⚙️ **Dashka** (`/dashka проблема`)
• Техническая поддержка
• Диагностика ошибок
• Решение проблем
• Конфигурация

**Советы:**
• Формулируйте задачи четко
• Приложите код если нужно
• Используйте контекст предыдущих сообщений"""
        
        await update.message.reply_markdown_v2(self._escape_markdown(help_text))
    
    async def _handle_status(self, update, context):
        """Команда /status"""
        from core.orchestrator import Orchestrator
        
        orchestrator = Orchestrator()
        
        # Получаем статус провайдеров
        status = await orchestrator.get_provider_status()
        stats = orchestrator.get_usage_stats()
        
        status_text = "📊 **Статус AI Solar 2.0**\n\n"
        
        status_text += "**Провайдеры:**\n"
        for provider, is_available in status.items():
            emoji = "✅" if is_available else "❌"
            status_text += f"• {emoji} {provider.title()}\n"
        
        status_text += "\n**Статистика использования:**\n"
        for provider, stat in stats.items():
            status_text += f"• {provider.title()}: {stat['requests']} запросов, {stat['tokens']} токенов\n"
        
        await update.message.reply_markdown_v2(self._escape_markdown(status_text))
    
    def _escape_markdown(self, text: str) -> str:
        """Экранирование для Markdown V2"""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    def run(self):
        """Запуск бота"""
        logger.info("🚀 Запускаем AI Solar 2.0...")
        self.application.run_polling()

def main():
    """Главная функция"""
    try:
        bot = AISolarBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()