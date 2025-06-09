#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой архитектуры AI Solar 2.0
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем корневую директорию в path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_architecture():
    """Тестирование архитектуры"""
    print("🧪 Тестирование архитектуры AI Solar 2.0...")
    print("=" * 50)
    
    # 1. Тест импортов
    print("1️⃣ Тестирование импортов...")
    try:
        from core.orchestrator import Orchestrator
        from core.ai_providers.claude import ClaudeProvider
        from core.ai_providers.deepseek import DeepSeekProvider
        from core.ai_providers.dashka import DashkaProvider
        from bot.handlers.claude import ClaudeHandler
        from bot.handlers.deepseek import DeepSeekHandler
        from bot.handlers.dashka import DashkaHandler
        print("✅ Все импорты успешны")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    
    # 2. Тест инициализации оркестратора
    print("\n2️⃣ Тестирование оркестратора...")
    try:
        orchestrator = Orchestrator()
        print(f"✅ Оркестратор создан с {len(orchestrator.providers)} провайдерами")
        
        # Проверяем статус провайдеров
        status = await orchestrator.get_provider_status()
        print("📊 Статус провайдеров:")
        for name, available in status.items():
            emoji = "✅" if available else "❌"
            print(f"   {emoji} {name}: {'доступен' if available else 'недоступен'}")
        
    except Exception as e:
        print(f"❌ Ошибка оркестратора: {e}")
        return False
    
    # 3. Тест хандлеров
    print("\n3️⃣ Тестирование хандлеров...")
    try:
        claude_handler = ClaudeHandler()
        deepseek_handler = DeepSeekHandler()
        dashka_handler = DashkaHandler()
        print("✅ Все хандлеры созданы")
    except Exception as e:
        print(f"❌ Ошибка хандлеров: {e}")
        return False
    
    # 4. Тест конфигурации
    print("\n4️⃣ Проверка конфигурации...")
    required_env_vars = [
        "TELEGRAM_BOT_TOKEN",
        "ANTHROPIC_API_KEY"
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        print("💡 Добавьте их в файл .env для полного функционала")
    else:
        print("✅ Все необходимые переменные окружения настроены")
    
    # 5. Тест базы данных (если доступна)
    print("\n5️⃣ Проверка базы данных...")
    try:
        from backend.database import engine
        from backend.models import Base
        
        # Проверяем подключение
        with engine.connect() as conn:
            print("✅ Подключение к базе данных успешно")
        
    except Exception as e:
        print(f"⚠️ База данных недоступна: {e}")
        print("💡 Настройте DATABASE_URL для работы с API")
    
    # 6. Тест простого запроса (если API ключи есть)
    print("\n6️⃣ Тест простого запроса...")
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            response = await orchestrator.process_request(
                provider_name="claude",
                query="Привет! Это тест архитектуры.",
                user_id=12345,
                chat_id=67890,
                context={"history": []}
            )
            
            if response.is_success:
                print("✅ Тестовый запрос выполнен успешно")
                print(f"📝 Ответ: {response.content[:100]}...")
            else:
                print(f"⚠️ Запрос завершен с ошибкой: {response.status}")
                
        except Exception as e:
            print(f"❌ Ошибка тестового запроса: {e}")
    else:
        print("⚠️ Пропускаем тест запроса (нет API ключа)")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование архитектуры завершено!")
    print("\n💡 Следующие шаги:")
    print("1. Настройте переменные окружения в .env")
    print("2. Запустите бот: python -m bot.bot")
    print("3. Запустите API: python -m backend.main")
    
    return True

def check_file_structure():
    """Проверка структуры файлов"""
    print("📁 Проверка структуры проекта...")
    
    required_files = [
        "bot/handlers/claude.py",
        "bot/handlers/deepseek.py", 
        "bot/handlers/dashka.py",
        "bot/handlers/base.py",
        "core/orchestrator.py",
        "core/ai_providers/claude.py",
        "core/ai_providers/deepseek.py",
        "core/ai_providers/dashka.py",
        "backend/main.py",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Отсутствуют файлы:")
        for file in missing_files:
            print(f"   • {file}")
        return False
    else:
        print("✅ Все необходимые файлы на месте")
        return True

async def main():
    """Главная функция тестирования"""
    print("🚀 AI Solar 2.0 - Тестирование архитектуры")
    print("=" * 50)
    
    # Проверяем структуру файлов
    if not check_file_structure():
        print("\n❌ Структура проекта неполная!")
        print("💡 Обновите файлы согласно новой архитектуре")
        return
    
    # Тестируем архитектуру
    await test_architecture()

if __name__ == "__main__":
    asyncio.run(main())