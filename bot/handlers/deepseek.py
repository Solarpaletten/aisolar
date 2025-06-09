# bot/handlers/deepseek.py - РОУТЕР для DeepSeek
"""
DeepSeek Handler - отвечает ТОЛЬКО за маршрутизацию команд программирования
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.orchestrator import Orchestrator
import logging

logger = logging.getLogger(__name__)

class DeepSeekHandler:
    """Роутер для DeepSeek команд - программирование и алгоритмы"""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основная команда /deepseek"""
        try:
            # Извлекаем текст запроса
            user_query = update.message.text.replace('/deepseek', '').strip()
            
            if not user_query:
                await self._show_help(update)
                return
            
            # Показываем статус
            await update.message.reply_chat_action("typing")
            status_msg = await update.message.reply_text("🔍 DeepSeek анализирует код...")
            
            # Делегируем обработку оркестратору
            response = await self.orchestrator.process_request(
                provider_name="deepseek",
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
            logger.error(f"DeepSeek handler error: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок DeepSeek"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("deepseek_"):
            action = callback_data.replace("deepseek_", "")
            
            # Делегируем обработку callback оркестратору
            response = await self.orchestrator.handle_callback(
                provider_name="deepseek",
                action=action,
                user_id=update.effective_user.id,
                context=self._extract_context(context)
            )
            
            await query.message.reply_text(response.content)
    
    def _extract_context(self, context: ContextTypes.DEFAULT_TYPE) -> dict:
        """Извлечение контекста из Telegram"""
        return {
            "history": context.user_data.get('deepseek_history', []),
            "user_data": context.user_data
        }
    
    async def _send_response(self, update: Update, response):
        """Отправка ответа пользователю"""
        # Форматируем сообщение для программирования
        text = f"🔍 **DeepSeek Code Analysis**\n\n{response.content}"
        
        # Добавляем метрики для кода
        if response.metadata:
            metrics = []
            if response.execution_time:
                metrics.append(f"⚡ {response.execution_time:.1f}с")
            if response.tokens_used:
                metrics.append(f"📊 {response.tokens_used} токенов")
            if response.metadata.get('complexity'):
                metrics.append(f"🔬 Сложность: {response.metadata['complexity']}")
            
            if metrics:
                text += f"\n\n*{' | '.join(metrics)}*"
        
        # Добавляем рекомендации по коду
        if response.suggestions:
            text += f"\n\n💡 **Рекомендации по коду:**\n"
            for i, suggestion in enumerate(response.suggestions[:3], 1):
                text += f"{i}. {suggestion}\n"
        
        # Создаем кнопки для программирования
        keyboard = self._create_programming_buttons(response)
        
        # Отправляем с обработкой длинных сообщений
        await self._send_formatted_message(update, text, keyboard)
    
    def _create_programming_buttons(self, response) -> InlineKeyboardMarkup:
        """Создание кнопок для программирования"""
        buttons = [
            [
                InlineKeyboardButton("🔧 Оптимизировать", callback_data="deepseek_optimize"),
                InlineKeyboardButton("🧪 Тестировать", callback_data="deepseek_test")
            ],
            [
                InlineKeyboardButton("📖 Документация", callback_data="deepseek_docs"),
                InlineKeyboardButton("🔍 Code Review", callback_data="deepseek_review")
            ],
            [
                InlineKeyboardButton("🐛 Debug", callback_data="deepseek_debug"),
                InlineKeyboardButton("📏 Рефакторинг", callback_data="deepseek_refactor")
            ]
        ]
        return InlineKeyboardMarkup(buttons)
    
    async def _send_formatted_message(self, update: Update, text: str, keyboard):
        """Отправка форматированного сообщения с обработкой кода"""
        try:
            # Проверяем наличие блоков кода
            if "```" in text:
                # Разбиваем на части если есть код
                parts = self._split_code_message(text)
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:  # Последняя часть с кнопками
                        await update.message.reply_markdown_v2(
                            self._escape_markdown(part),
                            reply_markup=keyboard
                        )
                    else:
                        await update.message.reply_markdown_v2(
                            self._escape_markdown(part)
                        )
            else:
                # Обычное сообщение
                await update.message.reply_markdown_v2(
                    self._escape_markdown(text),
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Error sending formatted message: {e}")
            # Fallback к простому тексту
            await update.message.reply_text(
                f"🔍 DeepSeek: {response.content}",
                reply_markup=keyboard
            )
    
    def _split_code_message(self, text: str) -> list:
        """Разбиение сообщения с кодом на части"""
        # Простая логика разбиения по блокам кода
        if len(text) <= 4000:
            return [text]
        
        # Если слишком длинное, разбиваем по абзацам
        paragraphs = text.split('\n\n')
        parts = []
        current_part = ""
        
        for paragraph in paragraphs:
            if len(current_part + paragraph) > 3500:
                if current_part:
                    parts.append(current_part)
                current_part = paragraph
            else:
                current_part += "\n\n" + paragraph if current_part else paragraph
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    async def _show_help(self, update: Update):
        """Показ справки по DeepSeek"""
        help_text = """🔍 **DeepSeek - Программирование и алгоритмы**

**Специализация:**
• 💻 Написание и анализ кода
• 🔧 Оптимизация алгоритмов
• 🧪 Создание тестов
• 🐛 Отладка и исправление ошибок
• 📖 Документирование кода

**Поддерживаемые языки:**
Python, JavaScript, Java, C++, Go, Rust, TypeScript

**Примеры запросов:**
• "Напиши быструю сортировку на Python"
• "Оптимизируй этот SQL запрос" + код
• "Найди ошибки в коде" + ваш код
• "Создай API для управления пользователями"
• "Напиши unit тесты для этой функции"

**Команды:**
• `/deepseek ваша_задача` - задать задачу программирования
• `/deepseek_history` - история решений

**Присылайте код, и я помогу его улучшить!** 🚀"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💡 Примеры", callback_data="deepseek_examples"),
                InlineKeyboardButton("⚙️ Настройки", callback_data="deepseek_settings")
            ]
        ])
        
        await update.message.reply_markdown_v2(
            self._escape_markdown(help_text),
            reply_markup=keyboard
        )
    
    def _escape_markdown(self, text: str) -> str:
        """Экранирование Markdown V2 с учетом блоков кода"""
        # Сначала защищаем блоки кода
        import re
        
        # Находим блоки кода и заменяем временными маркерами
        code_blocks = re.findall(r'```[\s\S]*?```', text)
        code_inline = re.findall(r'`[^`]*`', text)
        
        # Временные замены
        for i, block in enumerate(code_blocks):
            text = text.replace(block, f"__CODE_BLOCK_{i}__")
        
        for i, inline in enumerate(code_inline):
            text = text.replace(inline, f"__CODE_INLINE_{i}__")
        
        # Экранируем обычный текст
        chars = ['_', '*', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        
        # Возвращаем блоки кода
        for i, block in enumerate(code_blocks):
            text = text.replace(f"__CODE_BLOCK_{i}__", block)
        
        for i, inline in enumerate(code_inline):
            text = text.replace(f"__CODE_INLINE_{i}__", inline)
        
        return text

# Основные функции для регистрации
async def handle_deepseek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации команды /deepseek"""
    handler = DeepSeekHandler()
    await handler.handle_command(update, context)

async def handle_deepseek_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации callback"""
    handler = DeepSeekHandler()
    await handler.handle_callback(update, context)