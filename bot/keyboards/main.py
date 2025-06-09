# bot/keyboards/main_keyboard.py
from telegram import ReplyKeyboardMarkup, KeyboardButton
from core.ai_providers.base_provider import provider_registry
import asyncio
import logging

logger = logging.getLogger(__name__)

async def get_main_keyboard_with_status():
    """Главная клавиатура с актуальными статусами провайдеров"""
    try:
        # Получаем статусы всех провайдеров
        summary = await provider_registry.get_status_summary()
        providers = summary.get('providers', {})
        
        # Получаем статусы конкретных провайдеров
        dashka_info = providers.get('Dashka', {})
        claude_info = providers.get('Claude', {})
        
        dashka_status = dashka_info.get('status_emoji', '❓')
        claude_status = claude_info.get('status_emoji', '❓')
        
        # Статусы для будущих провайдеров
        deepseek_status = "🔄"  # В разработке
        grok_status = "⏳"      # Планируется
        
    except Exception as e:
        logger.warning(f"Ошибка получения статусов: {e}")
        # Fallback статусы
        dashka_status = "⚠️"
        claude_status = "⚠️" 
        deepseek_status = "🔄"
        grok_status = "⏳"
    
    # Формируем клавиатуру
    keyboard = [
        [
            f"🛠️ Dashka {dashka_status}",
            f"🧠 Claude {claude_status}"
        ],
        [
            f"💻 DeepSeek {deepseek_status}",
            f"🎨 Grok {grok_status}"
        ],
        [
            "📊 Статус системы",
            "📚 Справка"
        ],
        [
            "⚙️ Настройки"
        ]
    ]
    
    return keyboard

def get_ai_selection_keyboard():
    """Клавиатура выбора AI помощника"""
    keyboard = [
        [
            "🛠️ Техподдержка (Dashka)",
            "🧠 Анализ архитектуры (Claude)"
        ],
        [
            "💻 Генерация кода (DeepSeek)",
            "🎨 UI/UX дизайн (Grok)"
        ],
        [
            "🔍 Автоопределение",
            "🏠 Главное меню"
        ]
    ]
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = [
        [
            "🔔 Уведомления",
            "🌐 Язык интерфейса"
        ],
        [
            "💾 Экспорт истории",
            "🗑️ Очистить историю"
        ],
        [
            "🏠 Главное меню"
        ]
    ]
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def get_provider_status_text():
    """Получение текстового статуса всех провайдеров"""
    try:
        summary = await provider_registry.get_status_summary()
        
        status_text = "🤖 **Статус AI провайдеров:**\n\n"
        
        for provider_name, info in summary['providers'].items():
            emoji = info.get('emoji', '🤖')
            status_emoji = info.get('status_emoji', '❓')
            available = info.get('available', False)
            description = info.get('description', 'Описание недоступно')
            
            status_line = f"{emoji} **{provider_name}** {status_emoji}\n"
            status_line += f"   📝 {description}\n"
            status_line += f"   🟢 {'Активен' if available else 'Неактивен'}\n\n"
            
            status_text += status_line
        
        # Общая статистика
        total = summary.get('total', 0)
        available_count = summary.get('available', 0)
        
        status_text += f"📊 **Общая статистика:**\n"
        status_text += f"✅ Доступно: {available_count}/{total}\n"
        status_text += f"❌ Недоступно: {total - available_count}/{total}\n"
        
        return status_text
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        return "❌ Ошибка получения статуса провайдеров"

# bot/keyboards/__init__.py
from .main_keyboard import (
    get_main_keyboard_with_status,
    get_ai_selection_keyboard,
    get_settings_keyboard,
    get_provider_status_text
)

__all__ = [
    'get_main_keyboard_with_status',
    'get_ai_selection_keyboard', 
    'get_settings_keyboard',
    'get_provider_status_text'
]