# core/ai_providers/deepseek.py - ЧИСТЫЙ ПРОВАЙДЕР (только API)
"""
DeepSeek AI провайдер - ТОЛЬКО работа с DeepSeek API
Никакой бизнес-логики, только техническая интеграция
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import BaseAIProvider, AIProvider, AIResponse, AIResponseStatus

logger = logging.getLogger(__name__)

class DeepSeekProvider(BaseAIProvider):
    """Минимальный провайдер для DeepSeek API - только техническая интеграция"""
    
    def __init__(self):
        super().__init__(AIProvider.DEEPSEEK)
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
        self.max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000"))
        self.client = None
        
        if self.api_key and OPENAI_AVAILABLE:
            try:
                self.client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info("✅ DeepSeek API client инициализирован")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации DeepSeek: {e}")
        else:
            if not self.api_key:
                logger.warning("⚠️ DEEPSEEK_API_KEY не найден")
            if not OPENAI_AVAILABLE:
                logger.warning("⚠️ Модуль openai не установлен")
    
    async def is_available(self) -> bool:
        """Проверка доступности DeepSeek API"""
        if not self.client:
            self._is_available = False
            return False
        
        try:
            # Минимальный тест API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=10
                )
            )
            self._is_available = True
            self._last_check = datetime.now()
            return True
            
        except Exception as e:
            logger.error(f"❌ DeepSeek health check failed: {e}")
            self._is_available = False
            return False
    
    async def process(self, query: str, **kwargs) -> AIResponse:
        """
        Обработка запроса через DeepSeek API
        ТОЛЬКО техническая работа с API - никакой бизнес-логики!
        """
        start_time = datetime.now()
        
        if not self.client:
            return AIResponse(
                content="❌ DeepSeek API не настроен. Проверьте DEEPSEEK_API_KEY",
                provider=self.provider,
                status=AIResponseStatus.NOT_AVAILABLE,
                execution_time=0.1
            )
        
        try:
            # Извлекаем параметры
            system_prompt = kwargs.get("system_prompt", "You are a helpful coding assistant.")
            temperature = kwargs.get("temperature", 0.3)
            context = kwargs.get("context")
            
            # Подготавливаем сообщения
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Добавляем контекст если есть
            if context:
                messages.append({
                    "role": "user", 
                    "content": f"Context: {context}"
                })
            
            # Основной запрос
            messages.append({"role": "user", "content": query})
            
            # Выполняем запрос к DeepSeek API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=self.max_tokens,
                    temperature=temperature
                )
            )
            
            # Извлекаем контент
            content = ""
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Возвращаем ТОЛЬКО техническую информацию
            return AIResponse(
                content=content,
                provider=self.provider,
                status=AIResponseStatus.SUCCESS,
                model=self.model,
                execution_time=execution_time,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                cost=self._calculate_cost(response.usage) if response.usage else 0,
                metadata={
                    "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "output_tokens": response.usage.completion_tokens if response.usage else 0,
                    "finish_reason": response.choices[0].finish_reason if response.choices else None,
                    "model": self.model
                }
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"DeepSeek API error: {e}")
            return AIResponse(
                content=f"❌ Ошибка DeepSeek API: {str(e)}",
                provider=self.provider,
                status=AIResponseStatus.ERROR,
                execution_time=execution_time
            )
    
    def _calculate_cost(self, usage) -> float:
        """Расчет стоимости запроса (техническая функция)"""
        if not usage:
            return 0.0
        
        # Примерные цены DeepSeek ($/1K tokens)
        input_cost = (usage.prompt_tokens / 1000) * 0.0014
        output_cost = (usage.completion_tokens / 1000) * 0.0028
        return input_cost + output_cost