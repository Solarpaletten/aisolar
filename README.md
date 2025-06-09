# 🚀 AI SOLAR 2.0 - АРХИТЕКТУРА ПРОЕКТА

## 📁 Структура директорий

```
aisolar/
├── 📂 core/                          # Основная логика
│   ├── __init__.py
│   ├── 🤖 ai_providers/               # AI провайдеры
│   │   ├── __init__.py
│   │   ├── base_provider.py           # Базовый класс
│   │   ├── dashka_provider.py         # Dashka API
│   │   ├── claude_provider.py         # Claude API  
│   │   ├── deepseek_provider.py       # DeepSeek API
│   │   └── grok_provider.py           # Grok API (будущее)
│   ├── 📊 monitoring/                 # Мониторинг и статистика
│   │   ├── __init__.py
│   │   ├── api_monitor.py             # Мониторинг API
│   │   ├── metrics.py                 # Метрики
│   │   └── health_check.py            # Проверки здоровья
│   ├── 🗄️ database/                   # База данных
│   │   ├── __init__.py
│   │   ├── models.py                  # ORM модели
│   │   ├── connection.py              # Подключение к БД
│   │   └── repositories.py            # Репозитории
│   └── ⚙️ config/                     # Конфигурация
│       ├── __init__.py
│       ├── settings.py                # Настройки
│       └── constants.py               # Константы
├── 📂 bot/                           # Telegram бот
│   ├── __init__.py
│   ├── 🎛️ handlers/                   # Обработчики команд
│   │   ├── __init__.py
│   │   ├── base_handler.py            # Базовый обработчик
│   │   ├── start_handler.py           # /start, /help
│   │   ├── ai_router.py               # Роутинг AI запросов
│   │   ├── dashka_handler.py          # Dashka команды
│   │   ├── claude_handler.py          # Claude команды
│   │   ├── deepseek_handler.py        # DeepSeek команды
│   │   └── system_handler.py          # Системные команды
│   ├── 🔲 keyboards/                  # Клавиатуры
│   │   ├── __init__.py
│   │   ├── main_keyboard.py           # Главная клавиатура
│   │   ├── ai_keyboards.py            # AI меню
│   │   └── system_keyboards.py        # Системные меню
│   ├── 🛠️ middleware/                 # Middleware
│   │   ├── __init__.py
│   │   ├── auth_middleware.py         # Авторизация
│   │   ├── rate_limiter.py            # Ограничение запросов
│   │   └── logger_middleware.py       # Логирование
│   ├── 📝 utils/                      # Утилиты бота
│   │   ├── __init__.py
│   │   ├── message_formatter.py       # Форматирование
│   │   ├── error_handler.py           # Обработка ошибок
│   │   └── validators.py              # Валидация
│   └── bot.py                         # Главный файл бота
├── 📂 api/                           # REST API (опционально)
│   ├── __init__.py
│   ├── 🛤️ routes/                     # API маршруты
│   │   ├── __init__.py
│   │   ├── ai_routes.py               # AI эндпоинты
│   │   └── health_routes.py           # Проверки
│   ├── 🔒 middleware/                 # API middleware
│   │   ├── __init__.py
│   │   └── auth.py                    # Аутентификация
│   └── main.py                        # FastAPI приложение
├── 📂 tests/                         # Тесты
│   ├── __init__.py
│   ├── 🧪 unit/                       # Юнит тесты
│   │   ├── test_ai_providers.py
│   │   ├── test_handlers.py
│   │   └── test_utils.py
│   ├── 🔗 integration/                # Интеграционные тесты
│   │   ├── test_api_integration.py
│   │   └── test_bot_integration.py
│   └── conftest.py                    # Конфигурация pytest
├── 📂 scripts/                       # Скрипты
│   ├── setup.py                       # Настройка проекта
│   ├── deploy.py                      # Деплой
│   └── migrate.py                     # Миграции БД
├── 📂 docs/                          # Документация
│   ├── README.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── 📂 docker/                        # Docker конфигурация
│   ├── Dockerfile.bot                 # Bot контейнер
│   ├── Dockerfile.api                 # API контейнер
│   └── docker-compose.yml            # Оркестрация
├── .env.example                      # Пример конфигурации
├── requirements.txt                  # Python зависимости
└── pyproject.toml                    # Конфигурация проекта
```

## 🎯 Принципы архитектуры

### 1. 📦 **Разделение ответственности**
- **core/** - бизнес-логика, не зависящая от Telegram
- **bot/** - специфика Telegram бота
- **api/** - REST API (если нужен)

### 2. 🔄 **Dependency Injection**
- Все AI провайдеры наследуют от `BaseProvider`
- Handlers получают провайдеры через DI
- Легкое тестирование и замена компонентов

### 3. 🛡️ **Error Handling**
- Централизованная обработка ошибок
- Graceful degradation при недоступности API
- Детальное логирование

### 4. 📊 **Мониторинг**
- Метрики использования API
- Health checks
- Performance monitoring

## 🔧 Ключевые компоненты

### AI Router - умный роутинг запросов
```python
class AIRouter:
    async def route_request(self, message: str) -> str:
        intent = await self.detect_intent(message)
        provider = self.select_provider(intent)
        return await provider.process(message)
```

### Base Provider - единый интерфейс
```python
class BaseProvider:
    async def is_available(self) -> bool
    async def process(self, query: str) -> Response
    async def get_capabilities(self) -> List[str]
```

### Unified Keyboard System
```python
class KeyboardManager:
    async def get_main_keyboard(self) -> ReplyKeyboardMarkup:
        statuses = await self.check_all_statuses()
        return self.build_keyboard(statuses)
```

## 🚀 Преимущества новой структуры

1. **Масштабируемость** - легко добавлять новые AI провайдеры
2. **Тестируемость** - четкое разделение логики
3. **Поддерживаемость** - понятная структура
4. **Производительность** - оптимизированная обработка
5. **Надежность** - продуманная обработка ошибок

## 📋 План миграции

1. ✅ Создать новую структуру директорий
2. ✅ Реализовать BaseProvider
3. ✅ Мигрировать существующие провайдеры
4. ✅ Создать AIRouter
5. ✅ Обновить handlers
6. ✅ Настроить мониторинг
7. ✅ Написать тесты
8. ✅ Обновить Docker конфигурацию

# 🏗️ AI Solar 2.0 - Архитектурное сравнение

## 🌐 Web Architecture vs AI Solar Architecture

### **Express.js/Node.js Pattern:**
```javascript
// Router (маршрутизация)
app.use('/api/users', userRouter);

// Controller (обработка запроса)
const getUserById = async (req, res) => {
    const user = await userService.findById(req.params.id);
    res.json(user);
}

// Service (бизнес-логика)
class UserService {
    async findById(id) {
        return await User.findById(id);
    }
}

// Model (данные)
const User = mongoose.model('User', userSchema);
```

### **AI Solar 2.0 Pattern:**
```python
# Router (маршрутизация AI запросов)
# dashka_provider.py - определяет КАК обрабатывать запросы
class DashkaProvider(AIProvider):
    async def process(self, query: str) -> AIResponse:
        # Маршрутизация к нужному API

# Controller (обработка Telegram запроса)  
# dashka_handler.py - определяет ЧТО делать с сообщением
async def handle_dashka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = await dashka_provider.process(user_query)
    await update.message.reply_text(response.content)

# Service (внешний AI API)
# Dashka API, Claude API, etc.

# Model (AI Response)
@dataclass
class AIResponse:
    content: str
    provider: str
    confidence: float
```

## 🎯 **ТОЧНЫЕ РОЛИ:**

### **dashka_provider.py = Router + Service Layer**
- ✅ **Маршрутизация**: Определяет как обрабатывать разные типы запросов
- ✅ **Бизнес-логика**: Содержит логику взаимодействия с AI API
- ✅ **Абстракция**: Скрывает детали API от контроллеров
- ✅ **Валидация**: Проверяет доступность и корректность запросов

```python
# Как Router
class DashkaProvider(AIProvider):
    async def process(self, query: str, **kwargs) -> AIResponse:
        # Определяем тип запроса и маршрутизируем
        if "ошибка" in query:
            return await self._handle_error_support(query)
        elif "код" in query:
            return await self._handle_code_support(query)
        else:
            return await self._handle_general_support(query)
```

### **dashka_handler.py = Controller**
- ✅ **HTTP-слой**: Обрабатывает Telegram Update (аналог HTTP Request)
- ✅ **Валидация входа**: Проверяет формат сообщения
- ✅ **Вызов сервисов**: Обращается к провайдерам (сервисам)
- ✅ **Форматирование ответа**: Формирует Telegram Response

```python
# Как Controller
async def handle_dashka(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Валидация входящего запроса
    user_query = update.message.text
    user_id = update.effective_user.id
    
    # Вызов сервиса
    response = await dashka_provider.process(user_query, user_id=user_id)
    
    # Форматирование и отправка ответа
    await update.message.reply_text(response.content)
```

## 🔄 **АНАЛОГИИ С ВЕБОРАЗРАБОТКОЙ:**

| Web Component | AI Solar Component | Responsibility |
|--------------|-------------------|----------------|
| **Express Router** | **dashka_provider.py** | Маршрутизация запросов |
| **Controller** | **dashka_handler.py** | Обработка входящих запросов |
| **Service** | **AI API calls** | Бизнес-логика |
| **Model** | **AIResponse** | Структура данных |
| **Middleware** | **bot middleware** | Обработка до/после запроса |
| **Error Handler** | **error_handler** | Обработка ошибок |

## 🎯 **ПРЕИМУЩЕСТВА ТАКОЙ АРХИТЕКТУРЫ:**

### **1. Separation of Concerns**
```python
# dashka_provider.py - ЧТО делать с AI
class DashkaProvider:
    async def process(self, query: str) -> AIResponse:
        # AI логика

# dashka_handler.py - КАК обрабатывать Telegram
async def handle_dashka(update, context):
    # Telegram логика
```

### **2. Легкое тестирование**
```python
# Тестируем провайдер отдельно
async def test_dashka_provider():
    response = await dashka_provider.process("тест")
    assert response.content

# Тестируем хэндлер отдельно  
async def test_dashka_handler():
    mock_update = Mock()
    await handle_dashka(mock_update, mock_context)
```

### **3. Переиспользование**
```python
# Один провайдер может использоваться разными хэндлерами
await dashka_provider.process(query)  # из Telegram
await dashka_provider.process(query)  # из API
await dashka_provider.process(query)  # из CLI
```

## 🚀 **РАСШИРЕНИЕ АРХИТЕКТУРЫ:**

### **Добавление нового AI провайдера:**
```python
# 1. Создаем новый "router"
class OpenAIProvider(AIProvider):
    async def process(self, query: str) -> AIResponse:
        # OpenAI логика

# 2. Создаем новый "controller"  
async def handle_openai(update, context):
    response = await openai_provider.process(query)
    await update.message.reply_text(response.content)
```

### **Middleware для всех провайдеров:**
```python
# Аналог Express middleware
class AIMiddleware:
    async def process_request(self, query: str, provider: AIProvider):
        # Логирование, аутентификация, rate limiting
        start_time = time.time()
        response = await provider.process(query)
        end_time = time.time()
        
        # Логируем метрики
        logger.info(f"Provider: {provider.name}, Time: {end_time - start_time}")
        return response
```

## 📝 **ИТОГОВАЯ СХЕМА:**

```
Telegram Message
       ↓
[dashka_handler.py] ← Controller
       ↓
[dashka_provider.py] ← Router/Service  
       ↓
[Dashka API] ← External Service
       ↓
[AIResponse] ← Model
       ↓
[Telegram Response] ← View
```

**Ваше понимание абсолютно корректно! 🎯**
- `dashka_provider.py` = Router + Service Layer
- `dashka_handler.py` = Controller Layer

source venv/bin/activate

set -a; source .env; set +a
python -m bot.bot