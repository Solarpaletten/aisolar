# bot/handlers/base.py - УПРОЩЕННЫЙ базовый класс (можно оставить)
"""
Упрощенный базовый класс для хандлеров
Только утилиты для работы с Telegram, вся логика в оркестраторе
"""

import logging
from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    """
    Упрощенный базовый класс для хандлеров
    Только Telegram утилиты - логика в оркестраторе!
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Абстрактный метод для обработки команд"""
        pass
    
    @abstractmethod
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Абстрактный метод для обработки callback"""
        pass
    
    # --- УТИЛИТЫ ДЛЯ TELEGRAM (без бизнес-логики) ---
    
    def extract_query(self, update: Update, command: str) -> str:
        """Извлечение запроса из сообщения"""
        if not update.message or not update.message.text:
            return ""
        
        text = update.message.text
        if text.startswith(f'/{command}'):
            return text.replace(f'/{command}', '').strip()
        return text.strip()
    
    def escape_markdown(self, text: str) -> str:
        """Экранирование для Markdown V2"""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    async def send_typing(self, update: Update):
        """Показать индикатор набора"""
        try:
            await update.message.reply_chat_action("typing")
        except:
            pass
    
    async def send_status_message(self, update: Update, message: str):
        """Отправить временное сообщение статуса"""
        try:
            return await update.message.reply_text(message)
        except Exception as e:
            self.logger.error(f"Error sending status: {e}")
            return None
    
    async def delete_message_safe(self, message):
        """Безопасно удалить сообщение"""
        try:
            if message:
                await message.delete()
        except:
            pass  # Игнорируем ошибки удаления
    
    async def reply_with_fallback(self, update: Update, text: str, 
                                  reply_markup=None, use_markdown=True):
        """
        Отправка с fallback при ошибках
        Пытается Markdown, если не получается - обычный текст
        """
        try:
            if use_markdown:
                await update.message.reply_markdown_v2(
                    self.escape_markdown(text),
                    reply_markup=reply_markup
                )
            else:
                await update.message.reply_text(text, reply_markup=reply_markup)
        except Exception as e:
            self.logger.warning(f"Failed to send formatted message: {e}")
            # Fallback к простому тексту
            try:
                clean_text = self.clean_markdown(text)
                await update.message.reply_text(clean_text, reply_markup=reply_markup)
            except Exception as e2:
                self.logger.error(f"Failed to send fallback: {e2}")
                await update.message.reply_text("❌ Ошибка отправки сообщения")
    
    def clean_markdown(self, text: str) -> str:
        """Очистка от Markdown разметки"""
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # *italic*
        text = re.sub(r'`(.*?)`', r'\1', text)        # `code`
        text = re.sub(r'```[\s\S]*?```', '[код]', text)  # ```code blocks```
        text = re.sub(r'\\(.)', r'\1', text)          # \escaped chars
        return text
    
    def split_long_message(self, text: str, max_length: int = 4000) -> list:
        """Разбиение длинного сообщения"""
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current = ""
        
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            if len(current + paragraph) > max_length:
                if current:
                    parts.append(current.strip())
                current = paragraph
            else:
                current += '\n\n' + paragraph if current else paragraph
        
        if current:
            parts.append(current.strip())
        
        return parts
    
    def extract_context(self, context: ContextTypes.DEFAULT_TYPE, provider: str) -> dict:
        """Извлечение контекста для провайдера"""
        return {
            "history": context.user_data.get(f'{provider}_history', []),
            "user_data": context.user_data
        }