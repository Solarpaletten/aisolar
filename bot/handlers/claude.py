# bot/handlers/claude.py - РОУТЕР (только маршрутизация)
"""
Claude Handler - отвечает ТОЛЬКО за маршрутизацию Telegram команд
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.orchestrator import Orchestrator
import logging

logger = logging.getLogger(__name__)

class ClaudeHandler:
    """Роутер для Claude команд - только маршрутизация!"""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основная команда /claude"""
        try:
            # Извлекаем текст запроса
            user_query = update.message.text.replace('/claude', '').strip()
            
            if not user_query:
                await self._show_help(update)
                return
            
            # Показываем статус
            await update.message.reply_chat_action("typing")
            status_msg = await update.message.reply_text("🧠 Анализирую запрос...")
            
            # Делегируем обработку оркестратору
            response = await self.orchestrator.process_request(
                provider_name="claude",
                query=user_query,
                user_id=update.effective_user.id,
                chat_id=update.effective_chat.id,
                context=self._extract_context(context)
            )
            
            # Удаляем статус
            try:
                await status_msg.delete()
            except:
                pass
            
            # Отправляем ответ
            await self._send_response(update, response)
            
        except Exception as e:
            logger.error(f"Claude handler error: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("claude_"):
            action = callback_data.replace("claude_", "")
            
            # Делегируем обработку callback оркестратору
            response = await self.orchestrator.handle_callback(
                provider_name="claude",
                action=action,
                user_id=update.effective_user.id,
                context=self._extract_context(context)
            )
            
            await query.message.reply_text(response.content)
    
    def _extract_context(self, context: ContextTypes.DEFAULT_TYPE) -> dict:
        """Извлечение контекста из Telegram"""
        return {
            "history": context.user_data.get('claude_history', []),
            "user_data": context.user_data
        }
    
    async def _send_response(self, update: Update, response):
        """Отправка ответа пользователю"""
        # Форматируем сообщение
        text = f"🧠 **Claude Analysis**\n\n{response.content}"
        
        if response.metadata:
            if response.execution_time:
                text += f"\n\n⚡ {response.execution_time:.1f}с"
            if response.tokens_used:
                text += f" | 📊 {response.tokens_used} токенов"
        
        # Создаем кнопки
        keyboard = self._create_buttons(response)
        
        # Отправляем
        try:
            await update.message.reply_markdown_v2(
                self._escape_markdown(text),
                reply_markup=keyboard
            )
        except:
            # Fallback без markdown
            await update.message.reply_text(text, reply_markup=keyboard)
    
    def _create_buttons(self, response) -> InlineKeyboardMarkup:
        """Создание inline кнопок"""
        buttons = [
            [
                InlineKeyboardButton("🔄 Уточнить", callback_data="claude_clarify"),
                InlineKeyboardButton("🔍 Углубить", callback_data="claude_deeper")
            ],
            [
                InlineKeyboardButton("⚡ Производительность", callback_data="claude_performance"),
                InlineKeyboardButton("🔒 Безопасность", callback_data="claude_security")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    async def _show_help(self, update: Update):
        """Показ справки"""
        help_text = """🧠 **Claude - Архитектурный анализ**

**Использование:**
`/claude ваш_вопрос`

**Примеры:**
• "Как спроектировать микросервисную архитектуру?"
• "Сравни PostgreSQL vs MongoDB"
• "Оцени архитектуру этого API" + код

**Просто опишите задачу!** ✨"""
        
        await update.message.reply_markdown_v2(self._escape_markdown(help_text))
    
    def _escape_markdown(self, text: str) -> str:
        """Экранирование Markdown V2"""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text

# Основные функции для регистрации
async def handle_claude(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации команды /claude"""
    handler = ClaudeHandler()
    await handler.handle_command(update, context)

async def handle_claude_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации callback"""
    handler = ClaudeHandler()
    await handler.handle_callback(update, context)