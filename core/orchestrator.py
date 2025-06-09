# core/orchestrator.py - КОНТРОЛЛЕР с бизнес-логикой
"""
Orchestrator - ВСЯ бизнес-логика здесь!
Провайдеры только работают с API, оркестратор - думает
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .ai_providers.claude import ClaudeProvider
from .ai_providers.deepseek import DeepSeekProvider
from .ai_providers.dashka import DashkaProvider
from .ai_providers.base import AIResponse, AIResponseStatus

logger = logging.getLogger(__name__)

@dataclass
class RequestContext:
    """Контекст запроса"""
    user_id: int
    chat_id: int
    history: list
    user_data: dict
    timestamp: datetime

class Orchestrator:
    """
    Центральный оркестратор - ВСЯ бизнес-логика здесь!
    Провайдеры только работают с API
    """
    
    def __init__(self):
        # Инициализируем провайдеры (они только техническая часть)
        self.providers = {
            "claude": ClaudeProvider(),
            "deepseek": DeepSeekProvider(), 
            "dashka": DashkaProvider()
        }
        
        # Бизнес-логика оркестратора
        self.cache = {}
        self.usage_stats = {
            "claude": {"requests": 0, "tokens": 0, "errors": 0},
            "deepseek": {"requests": 0, "tokens": 0, "errors": 0},
            "dashka": {"requests": 0, "tokens": 0, "errors": 0}
        }
        
        # Системные промпты (БИЗНЕС-ЛОГИКА)
        self.system_prompts = {
            "claude": {
                "architecture": "Ты эксперт-архитектор ПО. Анализируй архитектурные решения, предлагай оптимальные паттерны, оценивай масштабируемость и производительность.",
                "technology": "Ты консультант по технологиям. Помогай с выбором tech stack, сравнивай подходы, анализируй плюсы и минусы решений.",
                "general": "Ты старший технический консультант. Отвечай структурированно и предоставляй практические советы."
            },
            "deepseek": {
                "programming": "Ты эксперт-программист. Пиши чистый, эффективный код. Оптимизируй алгоритмы и следуй best practices.",
                "code_review": "Ты code reviewer. Анализируй код на качество, безопасность, производительность. Предлагай конкретные улучшения.",
                "debugging": "Ты эксперт по отладке. Помогай находить и исправлять ошибки, объясняй причины проблем."
            },
            "dashka": {
                "support": "Ты технический специалист поддержки. Диагностируй проблемы системно, предлагай пошаговые решения.",
                "emergency": "Ты специалист экстренной поддержки. Приоритизируй критичные проблемы, давай быстрые решения."
            }
        }
    
    async def process_request(self, provider_name: str, query: str, 
                            user_id: int, chat_id: int, context: dict) -> AIResponse:
        """
        Основная бизнес-логика обработки запросов
        ТУТ принимаются все умные решения!
        """
        try:
            # 1. БИЗНЕС-ЛОГИКА: Создаем контекст
            request_context = RequestContext(
                user_id=user_id,
                chat_id=chat_id,
                history=context.get("history", []),
                user_data=context.get("user_data", {}),
                timestamp=datetime.now()
            )
            
            # 2. БИЗНЕС-ЛОГИКА: Проверяем провайдер
            provider = self.providers.get(provider_name)
            if not provider:
                return self._create_error_response(f"Провайдер {provider_name} не найден")
            
            if not await provider.is_available():
                return self._create_error_response(f"{provider_name} временно недоступен")
            
            # 3. БИЗНЕС-ЛОГИКА: Кэширование
            cache_key = self._generate_cache_key(provider_name, query, user_id)
            if cache_key in self.cache:
                logger.info(f"Cache hit for {provider_name}")
                cached_response = self.cache[cache_key]
                self._update_cache_metadata(cached_response)
                return cached_response
            
            # 4. БИЗНЕС-ЛОГИКА: Анализ типа запроса и подготовка промпта
            analysis_type = self._analyze_query_type(provider_name, query)
            system_prompt = self._get_system_prompt(provider_name, analysis_type)
            
            # 5. БИЗНЕС-ЛОГИКА: Подготовка параметров для провайдера
            provider_params = self._prepare_provider_params(
                provider_name, query, request_context, system_prompt
            )
            
            # 6. ТЕХНИЧЕСКАЯ ЧАСТЬ: Вызов провайдера (он только работает с API)
            response = await provider.process(query, **provider_params)
            
            # 7. БИЗНЕС-ЛОГИКА: Обогащение ответа
            enriched_response = self._enrich_response(
                response, provider_name, analysis_type, request_context
            )
            
            # 8. БИЗНЕС-ЛОГИКА: Обновление статистики и кэша
            self._update_stats(provider_name, enriched_response)
            
            if enriched_response.is_success:
                self.cache[cache_key] = enriched_response
                self._cleanup_cache_if_needed()
            
            # 9. БИЗНЕС-ЛОГИКА: Сохранение в историю
            self._save_to_history(request_context, query, enriched_response)
            
            return enriched_response
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return self._create_error_response(f"Ошибка обработки: {str(e)}")
    
    def _analyze_query_type(self, provider_name: str, query: str) -> str:
        """БИЗНЕС-ЛОГИКА: Анализ типа запроса"""
        query_lower = query.lower()
        
        if provider_name == "claude":
            if any(word in query_lower for word in ['архитектур', 'дизайн', 'паттерн']):
                return "architecture"
            elif any(word in query_lower for word in ['технолог', 'выбор', 'сравни']):
                return "technology"
            else:
                return "general"
                
        elif provider_name == "deepseek":
            if any(word in query_lower for word in ['код', 'code', 'функция']):
                return "programming"
            elif any(word in query_lower for word in ['ошибка', 'bug', 'debug']):
                return "debugging"
            elif any(word in query_lower for word in ['review', 'проверь', 'анализ']):
                return "code_review"
            else:
                return "programming"
                
        elif provider_name == "dashka":
            if any(word in query_lower for word in ['критично', 'urgent', 'экстренно']):
                return "emergency"
            else:
                return "support"
        
        return "general"
    
    def _get_system_prompt(self, provider_name: str, analysis_type: str) -> str:
        """БИЗНЕС-ЛОГИКА: Получение системного промпта"""
        provider_prompts = self.system_prompts.get(provider_name, {})
        return provider_prompts.get(analysis_type, provider_prompts.get("general", ""))
    
    def _prepare_provider_params(self, provider_name: str, query: str, 
                                context: RequestContext, system_prompt: str) -> dict:
        """БИЗНЕС-ЛОГИКА: Подготовка параметров для провайдера"""
        params = {
            "system_prompt": system_prompt,
            "context": self._format_context_for_provider(context),
            "user_id": context.user_id
        }
        
        # Специфичные настройки для разных провайдеров
        if provider_name == "claude":
            params["temperature"] = 0.1  # Точность
        elif provider_name == "deepseek":
            params["temperature"] = 0.3  # Креативность для кода
        elif provider_name == "dashka":
            params["temperature"] = 0.1  # Точность для техподдержки
        
        return params
    
    def _enrich_response(self, response: AIResponse, provider_name: str, 
                        analysis_type: str, context: RequestContext) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Обогащение ответа"""
        if not response.metadata:
            response.metadata = {}
        
        # Добавляем бизнес-метаданные
        response.metadata.update({
            "analysis_type": analysis_type,
            "processed_by": "orchestrator",
            "timestamp": context.timestamp.isoformat(),
            "user_id": context.user_id,
            "provider_name": provider_name
        })
        
        # БИЗНЕС-ЛОГИКА: Генерация рекомендаций
        if not response.suggestions:
            response.suggestions = self._generate_suggestions(
                response.content, provider_name, analysis_type
            )
        
        # БИЗНЕС-ЛОГИКА: Расчет уверенности
        if response.confidence == 0.0:
            response.confidence = self._calculate_confidence(
                response.content, provider_name
            )
        
        return response
    
    def _generate_suggestions(self, content: str, provider_name: str, 
                            analysis_type: str) -> List[str]:
        """БИЗНЕС-ЛОГИКА: Генерация рекомендаций"""
        suggestions = []
        
        if provider_name == "claude":
            if analysis_type == "architecture":
                suggestions = [
                    "Рассмотрите паттерны масштабирования",
                    "Проанализируйте требования к производительности",
                    "Оцените сложность поддержки"
                ]
            elif analysis_type == "technology":
                suggestions = [
                    "Сравните производительность решений",
                    "Оцените экосистему и поддержку",
                    "Проверьте совместимость с текущим стеком"
                ]
        
        elif provider_name == "deepseek":
            suggestions = [
                "Добавьте unit тесты",
                "Проверьте производительность алгоритма",
                "Рассмотрите обработку граничных случаев"
            ]
        
        elif provider_name == "dashka":
            suggestions = [
                "Проверьте логи системы",
                "Мониторьте ресурсы сервера",
                "Создайте backup перед изменениями"
            ]
        
        return suggestions[:3]  # Максимум 3 рекомендации
    
    def _calculate_confidence(self, content: str, provider_name: str) -> float:
        """БИЗНЕС-ЛОГИКА: Расчет уверенности"""
        if not content:
            return 0.0
        
        confidence = 0.5  # Базовая уверенность
        
        # Качественные индикаторы
        quality_words = ["рекомендую", "предлагаю", "оптимально", "лучше"]
        for word in quality_words:
            if word in content.lower():
                confidence += 0.05
        
        # Структурированность
        if any(marker in content for marker in ["1.", "•", "**"]):
            confidence += 0.1
        
        # Длина (детальность)
        if len(content) > 500:
            confidence += 0.1
        if len(content) > 1000:
            confidence += 0.1
        
        return min(confidence, 0.95)
    
    async def handle_callback(self, provider_name: str, action: str, 
                            user_id: int, context: dict) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Обработка callback действий"""
        try:
            provider = self.providers.get(provider_name)
            if not provider:
                return self._create_error_response(f"Провайдер {provider_name} не найден")
            
            # БИЗНЕС-ЛОГИКА: Обработка различных действий
            if action == "clarify":
                return await self._handle_clarify_action(provider, context)
            elif action == "deeper" or action == "optimize":
                return await self._handle_deeper_analysis(provider, context, action)
            elif action == "performance":
                return await self._handle_performance_analysis(provider, context)
            elif action == "security":
                return await self._handle_security_analysis(provider, context)
            else:
                return self._create_error_response(f"Неизвестное действие: {action}")
                
        except Exception as e:
            logger.error(f"Callback handler error: {e}")
            return self._create_error_response(f"Ошибка обработки действия: {str(e)}")
    
    async def _handle_clarify_action(self, provider, context: dict) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Обработка уточнения"""
        history = context.get("history", [])
        if not history:
            return self._create_error_response("Нет истории для уточнения")
        
        last_query = history[-1].get('query', '')
        clarify_prompt = f"Уточни и дополни анализ для запроса: {last_query}"
        
        return await provider.process(clarify_prompt, temperature=0.1)
    
    async def _handle_deeper_analysis(self, provider, context: dict, action: str) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Углубленный анализ"""
        history = context.get("history", [])
        if not history:
            return self._create_error_response("Нет истории для углубления")
        
        last_query = history[-1].get('query', '')
        
        if action == "optimize":
            prompt = f"Предложи оптимизации и улучшения для: {last_query}"
        else:
            prompt = f"Проведи углубленный анализ с техническими деталями для: {last_query}"
        
        return await provider.process(prompt, temperature=0.1)
    
    async def _handle_performance_analysis(self, provider, context: dict) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Анализ производительности"""
        history = context.get("history", [])
        if not history:
            return self._create_error_response("Нет истории для анализа производительности")
        
        last_query = history[-1].get('query', '')
        perf_prompt = f"Проанализируй производительность и оптимизацию для: {last_query}"
        
        return await provider.process(perf_prompt, temperature=0.1)
    
    async def _handle_security_analysis(self, provider, context: dict) -> AIResponse:
        """БИЗНЕС-ЛОГИКА: Анализ безопасности"""
        history = context.get("history", [])
        if not history:
            return self._create_error_response("Нет истории для анализа безопасности")
        
        last_query = history[-1].get('query', '')
        security_prompt = f"Проанализируй безопасность и уязвимости для: {last_query}"
        
        return await provider.process(security_prompt, temperature=0.1)
    
    def _format_context_for_provider(self, context: RequestContext) -> Optional[str]:
        """БИЗНЕС-ЛОГИКА: Форматирование контекста"""
        if not context.history:
            return None
            
        recent_history = context.history[-2:]  # Последние 2 записи
        
        formatted_context = "Предыдущие запросы:\n"
        for i, entry in enumerate(recent_history, 1):
            query = entry.get('query', '')[:100]
            formatted_context += f"{i}. {query}\n"
        
        return formatted_context
    
    def _generate_cache_key(self, provider: str, query: str, user_id: int) -> str:
        """Генерация ключа кэша"""
        import hashlib
        content = f"{provider}:{query[:200]}:{user_id}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _cleanup_cache_if_needed(self):
        """Очистка кэша при переполнении"""
        max_cache_size = 100
        if len(self.cache) > max_cache_size:
            # Удаляем половину старых записей
            items = list(self.cache.items())
            for key, _ in items[:len(items)//2]:
                del self.cache[key]
    
    def _update_stats(self, provider_name: str, response: AIResponse):
        """Обновление статистики"""
        if provider_name in self.usage_stats:
            self.usage_stats[provider_name]["requests"] += 1
            if response.tokens_used:
                self.usage_stats[provider_name]["tokens"] += response.tokens_used
            if not response.is_success:
                self.usage_stats[provider_name]["errors"] += 1
    
    def _save_to_history(self, context: RequestContext, query: str, response: AIResponse):
        """БИЗНЕС-ЛОГИКА: Сохранение в историю"""
        if "history" not in context.user_data:
            context.user_data["history"] = []
        
        history_entry = {
            "query": query,
            "response": response.content[:500],
            "provider": response.provider.value if response.provider else "unknown",
            "timestamp": context.timestamp.isoformat(),
            "tokens_used": response.tokens_used,
            "execution_time": response.execution_time
        }
        
        context.user_data["history"].append(history_entry)
        
        # Ограничиваем историю
        max_history = 20
        if len(context.user_data["history"]) > max_history:
            context.user_data["history"] = context.user_data["history"][-max_history:]
    
    def _create_error_response(self, message: str) -> AIResponse:
        """Создание ответа об ошибке"""
        from .ai_providers.base import AIResponse, AIResponseStatus
        return AIResponse(
            content=message,
            provider=None,
            status=AIResponseStatus.ERROR,
            execution_time=0.1
        )
    
    def _update_cache_metadata(self, response: AIResponse):
        """Обновление метаданных кэшированного ответа"""
        if response.metadata:
            response.metadata["from_cache"] = True
    
    async def get_provider_status(self) -> Dict[str, bool]:
        """Получение статуса всех провайдеров"""
        status = {}
        
        tasks = []
        for name, provider in self.providers.items():
            tasks.append(self._check_provider_status(name, provider))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, (name, _) in enumerate(self.providers.items()):
            status[name] = results[i] if not isinstance(results[i], Exception) else False
        
        return status
    
    async def _check_provider_status(self, name: str, provider) -> bool:
        """Проверка статуса одного провайдера"""
        try:
            return await provider.is_available()
        except:
            return False
    
    def get_usage_stats(self) -> Dict[str, Dict[str, int]]:
        """Получение статистики использования"""
        return self.usage_stats.copy()