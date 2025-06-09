# core/ai_providers/base.py - БАЗОВЫЕ КЛАССЫ (обязательно нужен!)
"""
Базовые классы для всех AI провайдеров
Определяет общий интерфейс и структуры данных
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Перечисление доступных AI провайдеров"""
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    DASHKA = "dashka"
    GPT4 = "gpt4"  # На будущее
    GEMINI = "gemini"  # На будущее

class AIResponseStatus(Enum):
    """Статусы ответов AI"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    NOT_AVAILABLE = "not_available"
    PARTIAL = "partial"

@dataclass
class AIResponse:
    """Универсальная структура ответа от AI провайдера"""
    
    # Основные поля
    content: str
    provider: Optional[AIProvider]
    status: AIResponseStatus
    
    # Технические метрики
    execution_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    model: str = ""
    
    # Дополнительные данные
    confidence: float = 0.0
    suggestions: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    
    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_success(self) -> bool:
        """Проверка успешности ответа"""
        return self.status == AIResponseStatus.SUCCESS
    
    @property
    def status_emoji(self) -> str:
        """Эмодзи для статуса"""
        status_emojis = {
            AIResponseStatus.SUCCESS: "✅",
            AIResponseStatus.ERROR: "❌",
            AIResponseStatus.TIMEOUT: "⏱️",
            AIResponseStatus.RATE_LIMITED: "🚫",
            AIResponseStatus.NOT_AVAILABLE: "🚧",
            AIResponseStatus.PARTIAL: "⚠️"
        }
        return status_emojis.get(self.status, "❓")
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            "content": self.content,
            "provider": self.provider.value if self.provider else None,
            "status": self.status.value,
            "execution_time": self.execution_time,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "model": self.model,
            "confidence": self.confidence,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

class BaseAIProvider(ABC):
    """
    Базовый класс для всех AI провайдеров
    Определяет общий интерфейс - провайдеры ТОЛЬКО работают с API!
    """
    
    def __init__(self, provider: AIProvider):
        self.provider = provider
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # Технические поля для мониторинга
        self._is_available = False
        self._last_check: Optional[datetime] = None
        self._error_count = 0
        self._total_requests = 0
        
        self.logger.info(f"🔧 Инициализирован провайдер: {provider.value}")
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Проверка доступности провайдера
        ТОЛЬКО техническая проверка API!
        """
        pass
    
    @abstractmethod
    async def process(self, query: str, **kwargs) -> AIResponse:
        """
        Обработка запроса через AI API
        ТОЛЬКО техническая работа с API - никакой бизнес-логики!
        
        Args:
            query: Текст запроса
            **kwargs: Дополнительные параметры (system_prompt, temperature, context и т.д.)
        
        Returns:
            AIResponse: Результат обработки
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики провайдера"""
        return {
            "provider": self.provider.value,
            "is_available": self._is_available,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "error_count": self._error_count,
            "total_requests": self._total_requests,
            "error_rate": self._error_count / max(1, self._total_requests)
        }
    
    def _increment_requests(self):
        """Увеличить счетчик запросов"""
        self._total_requests += 1
    
    def _increment_errors(self):
        """Увеличить счетчик ошибок"""
        self._error_count += 1
    
    def _reset_stats(self):
        """Сброс статистики"""
        self._error_count = 0
        self._total_requests = 0
        self._last_check = None

# Утилиты для работы с провайдерами
class ProviderUtils:
    """Утилиты для работы с провайдерами"""
    
    @staticmethod
    def create_success_response(
        content: str,
        provider: AIProvider,
        execution_time: float = 0.0,
        **kwargs
    ) -> AIResponse:
        """Создание успешного ответа"""
        return AIResponse(
            content=content,
            provider=provider,
            status=AIResponseStatus.SUCCESS,
            execution_time=execution_time,
            **kwargs
        )
    
    @staticmethod
    def create_error_response(
        error_message: str,
        provider: Optional[AIProvider] = None,
        execution_time: float = 0.0,
        status: AIResponseStatus = AIResponseStatus.ERROR
    ) -> AIResponse:
        """Создание ответа об ошибке"""
        return AIResponse(
            content=error_message,
            provider=provider,
            status=status,
            execution_time=execution_time
        )
    
    @staticmethod
    def validate_response(response: AIResponse) -> bool:
        """Валидация ответа"""
        if not response or not response.content:
            return False
        
        if response.status != AIResponseStatus.SUCCESS:
            return False
            
        return True
    
    @staticmethod
    def get_provider_by_name(name: str) -> Optional[AIProvider]:
        """Получение провайдера по имени"""
        try:
            return AIProvider(name.lower())
        except ValueError:
            return None

# Константы
DEFAULT_TIMEOUT = 30.0  # секунд
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.1

# Исключения
class ProviderError(Exception):
    """Базовое исключение провайдера"""
    pass

class ProviderNotAvailableError(ProviderError):
    """Провайдер недоступен"""
    pass

class ProviderTimeoutError(ProviderError):
    """Тайм-аут провайдера"""
    pass

class ProviderRateLimitError(ProviderError):
    """Превышен лимит запросов"""
    pass