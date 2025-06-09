# core/ai_providers/claude.py - ЧИСТЫЙ ПРОВАЙДЕР (только API)
"""
Claude AI провайдер - ТОЛЬКО работа с Anthropic API
Никакой бизнес-логики, только техническая интеграция
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import BaseAIProvider, AIProvider, AIResponse, AIResponseStatus

logger = logging.getLogger(__name__)

class ClaudeProvider(BaseAIProvider):
    """Минимальный провайдер для Claude API - только техническая интеграция"""
    
    def __init__(self):
        super().__init__(AIProvider.CLAUDE)
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
        self.max_tokens = int(os.getenv("CLAUDE_MAX_TOKENS", "4000"))
        self.client = None
        
        if self.api_key and ANTHROPIC_AVAILABLE:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info("✅ Claude API client инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Claude: {e}")
        else:
            if not self.api_key:
                logger.warning("⚠️ ANTHROPIC_API_KEY не найден")
            if not ANTHROPIC_AVAILABLE:
                logger.warning("⚠️ Модуль anthropic не установлен")
    
    async def is_available(self) -> bool:
        """Проверка доступности Claude API"""
        if not self.client:
            self._is_available = False
            return False
        
        try:
            # Минимальный тест API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=10,
                    messages=[{"role": "user", "content": "test"}]
                )
            )
            self._is_available = True
            self._last_check = datetime.now()
            return True
            
        except anthropic.RateLimitError:
            logger.warning("⏱️ Claude: Rate limit exceeded")
            self._is_available = False
            return False
        except Exception as e:
            logger.error(f"❌ Claude health check failed: {e}")
            self._is_available = False
            return False
    
    async def process(self, query: str, **kwargs) -> AIResponse:
        """
        Обработка запроса через Claude API
        ТОЛЬКО техническая работа с API - никакой бизнес-логики!
        """
        start_time = datetime.now()
        
        if not self.client:
            return AIResponse(
                content="❌ Claude API не настроен. Проверьте ANTHROPIC_API_KEY",
                provider=self.provider,
                status=AIResponseStatus.NOT_AVAILABLE,
                execution_time=0.1
            )
        
        try:
            # Извлекаем параметры
            system_prompt = kwargs.get("system_prompt", "")
            temperature = kwargs.get("temperature", 0.1)
            context = kwargs.get("context")
            
            # Подготавливаем сообщения
            messages = []
            
            # Добавляем контекст если есть
            if context:
                messages.append({
                    "role": "user",
                    "content": f"Контекст: {context}"
                })
            
            # Основной запрос
            messages.append({"role": "user", "content": query})
            
            # Выполняем запрос к Claude API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=temperature,
                    system=system_prompt if system_prompt else "Ты полезный AI ассистент.",
                    messages=messages
                )
            )
            
            # Извлекаем контент
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Возвращаем ТОЛЬКО техническую информацию
            return AIResponse(
                content=content,
                provider=self.provider,
                status=AIResponseStatus.SUCCESS,
                model=self.model,
                execution_time=execution_time,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=self._calculate_cost(response.usage),
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                    "model": self.model
                }
            )
            
        except anthropic.RateLimitError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return AIResponse(
                content="⏱️ Превышен лимит запросов к Claude API",
                provider=self.provider,
                status=AIResponseStatus.RATE_LIMITED,
                execution_time=execution_time
            )
            
        except anthropic.APITimeoutError:
            execution_time = (datetime.now() - start_time).total_seconds()
            return AIResponse(
                content="⏱️ Тайм-аут запроса к Claude API",
                provider=self.provider,
                status=AIResponseStatus.TIMEOUT,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Claude API error: {e}")
            return AIResponse(
                content=f"❌ Ошибка Claude API: {str(e)}",
                provider=self.provider,
                status=AIResponseStatus.ERROR,
                execution_time=execution_time
            )
    
    def _calculate_cost(self, usage) -> float:
        """Расчет стоимости запроса (техническая функция)"""
        # Примерные цены Claude ($/1K tokens)
        input_cost = (usage.input_tokens / 1000) * 0.003
        output_cost = (usage.output_tokens / 1000) * 0.015
        return input_cost + output_cost