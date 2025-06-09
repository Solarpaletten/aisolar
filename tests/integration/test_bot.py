#!/usr/bin/env python3
# test_bot.py - Минимальный бот для тестирования

import os
import asyncio
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_imports():
    """Тест импортов"""
    print("🧪 Тестирование импортов...")
    
    try:
        import telegram
        print("✅ telegram")
    except ImportError as e:
        print(f"❌ telegram: {e}")
        return False
    
    try:
        import anthropic
        print("✅ anthropic")
    except ImportError as e:
        print(f"❌ anthropic: {e}")
    
    try:
        import httpx
        print("✅ httpx")
    except ImportError as e:
        print(f"❌ httpx: {e}")
    
    return True

async def test_api_keys():
    """Тест API ключей"""
    print("\n🔑 Проверка API ключей...")
    
    bot_token = os.getenv('BOT_TOKEN', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    print(f"BOT_TOKEN: {'✅' if len(bot_token) > 40 else '❌'} ({len(bot_token)} символов)")
    print(f"ANTHROPIC_API_KEY: {'✅' if len(anthropic_key) > 40 else '❌'} ({len(anthropic_key)} символов)")
    
    return len(bot_token) > 40

async def test_bot_creation():
    """Тест создания бота"""
    print("\n🤖 Тестирование создания бота...")
    
    try:
        from telegram import Bot
        bot_token = os.getenv('BOT_TOKEN')
        
        if not bot_token:
            print("⚠️ BOT_TOKEN не найден")
            return False
        
        bot = Bot(token=bot_token)
        me = await bot.get_me()
        print(f"✅ Бот создан: @{me.username}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания бота: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🚀 AI SOLAR 2.0 - ТЕСТ СИСТЕМЫ")
    print("=" * 40)
    
    # Тест импортов
    imports_ok = await test_imports()
    
    if not imports_ok:
        print("\n❌ Критические модули не импортируются")
        print("Запустите: ./quick_fix.sh")
        return
    
    # Тест API ключей
    keys_ok = await test_api_keys()
    
    # Тест создания бота
    if keys_ok:
        bot_ok = await test_bot_creation()
    else:
        print("⚠️ Пропускаем тест бота - нет API ключей")
        bot_ok = False
    
    print("\n" + "=" * 40)
    print("📊 ИТОГОВЫЙ СТАТУС:")
    print(f"Импорты: {'✅' if imports_ok else '❌'}")
    print(f"API ключи: {'✅' if keys_ok else '❌'}")
    print(f"Telegram бот: {'✅' if bot_ok else '❌'}")
    
    if imports_ok and keys_ok and bot_ok:
        print("\n🎉 ВСЕ ГОТОВО! Можно запускать основной бот:")
        print("   python bot/bot.py")
    elif imports_ok and keys_ok:
        print("\n⚠️ Почти готово! Проверьте BOT_TOKEN и запустите снова")
    elif imports_ok:
        print("\n🔧 Настройте .env файл с API ключами")
    else:
        print("\n🚨 Нужно исправить проблемы с зависимостями")

if __name__ == "__main__":
    asyncio.run(main())
