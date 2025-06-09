# bot/handlers/dashka.py - РОУТЕР для Dashka  
"""
Dashka Handler - отвечает ТОЛЬКО за маршрутизацию команд техподдержки
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core.orchestrator import Orchestrator
import logging

logger = logging.getLogger(__name__)

class DashkaHandler:
    """Роутер для Dashka команд - техподдержка и диагностика"""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
    
    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основная команда /dashka"""
        try:
            # Извлекаем текст запроса
            user_query = update.message.text.replace('/dashka', '').strip()
            
            if not user_query:
                await self._show_help(update)
                return
            
            # Показываем статус
            await update.message.reply_chat_action("typing")
            status_msg = await update.message.reply_text("⚙️ Dashka диагностирует проблему...")
            
            # Делегируем обработку оркестратору
            response = await self.orchestrator.process_request(
                provider_name="dashka",
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
            logger.error(f"Dashka handler error: {e}")
            await update.message.reply_text(f"❌ Ошибка: {str(e)}")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок Dashka"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith("dashka_"):
            action = callback_data.replace("dashka_", "")
            
            # Специальная обработка для некоторых действий
            if action == "emergency":
                await self._handle_emergency(query)
                return
            elif action == "escalate":
                await self._handle_escalation(query, context)
                return
            
            # Обычная обработка через оркестратор
            response = await self.orchestrator.handle_callback(
                provider_name="dashka",
                action=action,
                user_id=update.effective_user.id,
                context=self._extract_context(context)
            )
            
            await query.message.reply_text(response.content)
    
    def _extract_context(self, context: ContextTypes.DEFAULT_TYPE) -> dict:
        """Извлечение контекста из Telegram"""
        return {
            "history": context.user_data.get('dashka_history', []),
            "user_data": context.user_data
        }
    
    async def _send_response(self, update: Update, response):
        """Отправка ответа пользователю"""
        # Форматируем сообщение для техподдержки
        text = f"⚙️ **Dashka Technical Support**\n\n{response.content}"
        
        # Добавляем приоритет и категорию
        if response.metadata:
            priority = response.metadata.get('priority', 'normal')
            category = response.metadata.get('category', 'general')
            
            priority_emoji = {
                'low': '🟢',
                'normal': '🟡', 
                'high': '🟠',
                'critical': '🔴'
            }
            
            emoji = priority_emoji.get(priority, '🟡')
            text += f"\n\n{emoji} **Приоритет:** {priority.title()}"
            text += f"\n🏷️ **Категория:** {category.title()}"
            
            # Добавляем время ответа
            if response.execution_time:
                text += f"\n⚡ **Время диагностики:** {response.execution_time:.1f}с"
        
        # Добавляем шаги решения
        if response.suggestions:
            text += f"\n\n🔧 **Шаги решения:**\n"
            for i, step in enumerate(response.suggestions[:5], 1):
                text += f"{i}. {step}\n"
        
        # Создаем кнопки техподдержки
        keyboard = self._create_support_buttons(response)
        
        # Отправляем
        try:
            await update.message.reply_markdown_v2(
                self._escape_markdown(text),
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Error sending Dashka response: {e}")
            # Fallback без markdown
            await update.message.reply_text(
                f"⚙️ Dashka: {response.content}",
                reply_markup=keyboard
            )
    
    def _create_support_buttons(self, response) -> InlineKeyboardMarkup:
        """Создание кнопок техподдержки"""
        buttons = []
        
        # Первый ряд - основные действия
        row1 = [
            InlineKeyboardButton("✅ Помогло", callback_data="dashka_solved"),
            InlineKeyboardButton("❌ Не помогло", callback_data="dashka_escalate")
        ]
        
        # Второй ряд - дополнительная диагностика
        row2 = [
            InlineKeyboardButton("🔍 Диагностика", callback_data="dashka_diagnose"),
            InlineKeyboardButton("📋 Логи", callback_data="dashka_logs")
        ]
        
        # Третий ряд - экстренные действия
        row3 = [
            InlineKeyboardButton("🚨 Экстренно", callback_data="dashka_emergency"),
            InlineKeyboardButton("📞 Связаться", callback_data="dashka_contact")
        ]
        
        buttons.extend([row1, row2, row3])
        
        # Добавляем специальные кнопки для критических проблем
        if response.metadata and response.metadata.get('priority') == 'critical':
            critical_row = [
                InlineKeyboardButton("🔥 КРИТИЧНО - НЕМЕДЛЕННО", callback_data="dashka_critical")
            ]
            buttons.insert(0, critical_row)
        
        return InlineKeyboardMarkup(buttons)
    
    async def _handle_emergency(self, query):
        """Обработка экстренных ситуаций"""
        emergency_text = """🚨 **ЭКСТРЕННАЯ ТЕХПОДДЕРЖКА**

**Немедленные действия:**
1. 🔴 Проверьте статус критических сервисов
2. 📊 Мониторинг системных ресурсов  
3. 💾 Создайте backup текущего состояния
4. 📞 Уведомите команду разработки

**Контакты экстренной поддержки:**
• Telegram: @tech_support_emergency
• Email: emergency@company.com
• Телефон: +1-800-EMERGENCY

**Система автоматически создала тикет с высоким приоритетом**"""
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Вызвать команду", callback_data="dashka_call_team")],
            [InlineKeyboardButton("📋 Создать отчет", callback_data="dashka_create_report")]
        ])
        
        await query.message.reply_markdown_v2(
            DashkaHandler()._escape_markdown(emergency_text),
            reply_markup=keyboard
        )
    
    async def _handle_escalation(self, query, context):
        """Обработка эскалации проблемы"""
        escalation_text = """📈 **ЭСКАЛАЦИЯ ПРОБЛЕМЫ**

Ваша проблема передана на следующий уровень поддержки.

**Что происходит дальше:**
1. 🎯 Назначен senior специалист
2. 📋 Создан приоритетный тикет
3. ⏰ SLA: ответ в течение 2 часов
4. 📧 Уведомления на email

**Номер тикета:** DASH-{user_id}-{timestamp}

**Следующие шаги:**
• Ожидайте контакта от специалиста
• Подготовьте дополнительную информацию
• Не перезапускайте системы без согласования"""
        
        # Генерируем номер тикета
        import time
        user_id = query.from_user.id
        timestamp = int(time.time())
        
        formatted_text = escalation_text.format(
            user_id=user_id,
            timestamp=timestamp
        )
        
        await query.message.reply_markdown_v2(
            DashkaHandler()._escape_markdown(formatted_text)
        )
    
    async def _show_help(self, update: Update):
        """Показ справки по Dashka"""
        help_text = """⚙️ **Dashka - Техническая поддержка**

**Специализация:**
• 🔧 Диагностика технических проблем
• 🚨 Экстренная поддержка
• 📊 Анализ логов и ошибок
• ⚙️ Настройка конфигураций
• 🔍 Поиск решений

**Типы проблем:**
• Ошибки сервера и приложений
• Проблемы с базами данных
• Сетевые неполадки
• Проблемы развертывания
• Вопросы конфигурации

**Примеры запросов:**
• "Сервер не отвечает на порту 8080"
• "База данных возвращает ошибку подключения"
• "Docker контейнер не запускается" + логи
• "Как настроить SSL сертификат?"
• "Анализируй этот лог ошибок" + логи

**Приоритеты:**
🟢 Низкий - общие вопросы
🟡 Обычный - рабочие проблемы  
🟠 Высокий - влияет на работу
🔴 Критический - система недоступна

**Команды:**
• `/dashka проблема` - описать проблему
• `/dashka_status` - статус системы

**Опишите проблему детально для быстрого решения!** 🛠️"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔧 Частые проблемы", callback_data="dashka_faq"),
                InlineKeyboardButton("📊 Статус системы", callback_data="dashka_system_status")
            ]
        ])
        
        await update.message.reply_markdown_v2(
            self._escape_markdown(help_text),
            reply_markup=keyboard
        )
    
    def _escape_markdown(self, text: str) -> str:
        """Экранирование Markdown V2"""
        chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in chars:
            text = text.replace(char, f'\\{char}')
        return text

# Основные функции для регистрации
async def handle_dashka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации команды /dashka"""
    handler = DashkaHandler()
    await handler.handle_command(update, context)

async def handle_dashka_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функция для регистрации callback"""
    handler = DashkaHandler()
    await handler.handle_callback(update, context)