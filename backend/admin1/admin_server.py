# admin/admin_server.py
"""
AI Solar 2.0 - Admin WebSocket Server
Мониторинг всех AI взаимодействий в реальном времени
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
import websockets
from dataclasses import dataclass, asdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIInteraction:
    """Структура AI взаимодействия"""
    id: str
    timestamp: datetime
    user_id: str
    sender: str  # user, dashka, claude, deepseek
    content: str
    metadata: Optional[Dict] = None
    
    def to_dict(self):
        """Конвертация в словарь для JSON"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'sender': self.sender,
            'content': self.content,
            'metadata': self.metadata or {}
        }

@dataclass
class RoutingEvent:
    """Событие маршрутизации"""
    timestamp: datetime
    type: str  # route, process, response, error
    message: str
    details: Optional[Dict] = None
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'type': self.type,
            'message': self.message,
            'details': self.details or {}
        }

@dataclass
class AIProviderStatus:
    """Статус AI провайдера"""
    name: str
    status: str  # online, offline, error
    last_response_time: Optional[float] = None
    success_rate: float = 0.0
    total_requests: int = 0
    
    def to_dict(self):
        return asdict(self)

class AdminWebSocketManager:
    """Менеджер WebSocket соединений для админки"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.interactions: List[AIInteraction] = []
        self.routing_events: List[RoutingEvent] = []
        self.ai_providers: Dict[str, AIProviderStatus] = {
            'dashka': AIProviderStatus('Dashka', 'online', 0.3, 0.95, 156),
            'claude': AIProviderStatus('Claude', 'online', 1.2, 0.94, 89),
            'deepseek': AIProviderStatus('DeepSeek', 'online', 0.8, 0.92, 67)
        }
        
    async def connect(self, websocket: WebSocket):
        """Подключение нового админа"""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Админ подключен. Всего: {len(self.active_connections)}")
        
        # Отправляем текущее состояние
        await self.send_initial_state(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Отключение админа"""
        self.active_connections.discard(websocket)
        logger.info(f"Админ отключен. Осталось: {len(self.active_connections)}")
    
    async def send_initial_state(self, websocket: WebSocket):
        """Отправка начального состояния"""
        try:
            initial_data = {
                'type': 'initial_state',
                'data': {
                    'interactions': [i.to_dict() for i in self.interactions[-50:]],  # Последние 50
                    'routing_events': [e.to_dict() for e in self.routing_events[-20:]],  # Последние 20
                    'ai_providers': {name: status.to_dict() for name, status in self.ai_providers.items()},
                    'stats': {
                        'total_messages': len(self.interactions),
                        'active_users': len(set(i.user_id for i in self.interactions[-100:])),
                        'avg_response_time': self._calculate_avg_response_time()
                    }
                }
            }
            await websocket.send_text(json.dumps(initial_data))
        except Exception as e:
            logger.error(f"Ошибка отправки начального состояния: {e}")
    
    async def broadcast_interaction(self, interaction: AIInteraction):
        """Рассылка нового взаимодействия всем админам"""
        self.interactions.append(interaction)
        
        # Ограничиваем историю
        if len(self.interactions) > 1000:
            self.interactions = self.interactions[-500:]
        
        message = {
            'type': 'new_interaction',
            'data': interaction.to_dict()
        }
        
        await self._broadcast(message)
    
    async def broadcast_routing_event(self, event: RoutingEvent):
        """Рассылка события маршрутизации"""
        self.routing_events.append(event)
        
        # Ограничиваем историю
        if len(self.routing_events) > 200:
            self.routing_events = self.routing_events[-100:]
        
        message = {
            'type': 'routing_event',
            'data': event.to_dict()
        }
        
        await self._broadcast(message)
    
    async def update_ai_provider_status(self, provider_name: str, status_update: Dict):
        """Обновление статуса AI провайдера"""
        if provider_name in self.ai_providers:
            provider = self.ai_providers[provider_name]
            
            # Обновляем поля
            if 'status' in status_update:
                provider.status = status_update['status']
            if 'last_response_time' in status_update:
                provider.last_response_time = status_update['last_response_time']
            if 'success_rate' in status_update:
                provider.success_rate = status_update['success_rate']
            if 'total_requests' in status_update:
                provider.total_requests = status_update['total_requests']
            
            message = {
                'type': 'provider_status_update',
                'data': {
                    'provider': provider_name,
                    'status': provider.to_dict()
                }
            }
            
            await self._broadcast(message)
    
    async def _broadcast