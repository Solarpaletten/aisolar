# backend/admin/modern_admin.py
"""
AI Solar 2.0 - Современная админ панель
Интегрирована с новой архитектурой оркестратора
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn

# Импорты новой архитектуры
from core.orchestrator import Orchestrator
from core.ai_providers.base import AIProvider, AIResponseStatus

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI приложение
app = FastAPI(title="AI Solar 2.0 Admin Dashboard")

# Подключаем статику и шаблоны
app.mount("/static", StaticFiles(directory="backend/admin/static"), name="static")
templates = Jinja2Templates(directory="backend/admin/templates")

# Оркестратор для получения данных
orchestrator = Orchestrator()

# WebSocket соединения
active_connections: List[WebSocket] = []

class AdminDashboard:
    """Класс для управления админ дашбордом"""
    
    def __init__(self):
        self.orchestrator = orchestrator
        self.active_connections = []
    
    async def get_dashboard_data(self) -> Dict:
        """Получение данных для дашборда"""
        try:
            # Статус провайдеров
            provider_status = await self.orchestrator.get_provider_status()
            
            # Статистика использования
            usage_stats = self.orchestrator.get_usage_stats()
            
            # Общая статистика
            total_requests = sum(stats["requests"] for stats in usage_stats.values())
            total_tokens = sum(stats["tokens"] for stats in usage_stats.values())
            total_errors = sum(stats["errors"] for stats in usage_stats.values())
            
            # Расчет метрик
            error_rate = (total_errors / max(total_requests, 1)) * 100
            avg_tokens_per_request = total_tokens / max(total_requests, 1)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overview": {
                    "total_requests": total_requests,
                    "total_tokens": total_tokens,
                    "total_errors": total_errors,
                    "error_rate": round(error_rate, 2),
                    "avg_tokens_per_request": round(avg_tokens_per_request, 1),
                    "active_providers": len([p for p, status in provider_status.items() if status])
                },
                "providers": {
                    name: {
                        "status": "online" if provider_status.get(name, False) else "offline",
                        "requests": usage_stats.get(name, {}).get("requests", 0),
                        "tokens": usage_stats.get(name, {}).get("tokens", 0),
                        "errors": usage_stats.get(name, {}).get("errors", 0),
                        "status_emoji": "✅" if provider_status.get(name, False) else "❌"
                    }
                    for name in ["claude", "deepseek", "dashka"]
                },
                "system": {
                    "cache_size": len(self.orchestrator.cache),
                    "uptime": "Running",  # TODO: реальный uptime
                    "memory_usage": "N/A"  # TODO: реальная память
                }
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}
    
    async def broadcast_update(self, data: Dict):
        """Рассылка обновлений всем подключенным клиентам"""
        if not self.active_connections:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for conn in disconnected:
            self.active_connections.remove(conn)

# Создаем экземпляр дашборда
dashboard = AdminDashboard()

# Маршруты
@app.get("/")
async def admin_dashboard(request: Request):
    """Главная страница админки"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/dashboard")
async def get_dashboard_data():
    """API для получения данных дашборда"""
    data = await dashboard.get_dashboard_data()
    return JSONResponse(data)

@app.get("/api/providers")
async def get_providers_status():
    """API статуса провайдеров"""
    status = await orchestrator.get_provider_status()
    stats = orchestrator.get_usage_stats()
    
    providers = {}
    for name in ["claude", "deepseek", "dashka"]:
        providers[name] = {
            "name": name.title(),
            "status": "online" if status.get(name, False) else "offline",
            "requests": stats.get(name, {}).get("requests", 0),
            "tokens": stats.get(name, {}).get("tokens", 0),
            "errors": stats.get(name, {}).get("errors", 0),
            "error_rate": (stats.get(name, {}).get("errors", 0) / 
                          max(stats.get(name, {}).get("requests", 1), 1)) * 100
        }
    
    return JSONResponse({"providers": providers})

@app.post("/api/test-provider/{provider_name}")
async def test_provider(provider_name: str):
    """Тестирование провайдера"""
    try:
        response = await orchestrator.process_request(
            provider_name=provider_name,
            query="Тест подключения из админ панели",
            user_id=999999,  # Админский тест
            chat_id=999999,
            context={"history": []}
        )
        
        return JSONResponse({
            "success": response.is_success,
            "response": response.content[:100] + "..." if len(response.content) > 100 else response.content,
            "execution_time": response.execution_time,
            "tokens_used": response.tokens_used,
            "status": response.status.value
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@app.get("/api/stats")
async def get_detailed_stats():
    """Подробная статистика"""
    stats = orchestrator.get_usage_stats()
    provider_status = await orchestrator.get_provider_status()
    
    return JSONResponse({
        "usage_stats": stats,
        "provider_status": provider_status,
        "cache_stats": {
            "size": len(orchestrator.cache),
            "keys": list(orchestrator.cache.keys())[:10]  # Первые 10 ключей
        },
        "timestamp": datetime.now().isoformat()
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket для real-time обновлений"""
    await websocket.accept()
    dashboard.active_connections.append(websocket)
    logger.info(f"WebSocket connected. Total connections: {len(dashboard.active_connections)}")
    
    try:
        # Отправляем начальные данные
        initial_data = await dashboard.get_dashboard_data()
        await websocket.send_text(json.dumps({
            "type": "initial_data",
            "data": initial_data
        }))
        
        # Ждем сообщения (keep alive)
        while True:
            try:
                data = await websocket.receive_text()
                # Эхо для keep alive
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        dashboard.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(dashboard.active_connections)}")

# Фоновая задача для периодических обновлений
async def periodic_updates():
    """Периодические обновления для WebSocket клиентов"""
    while True:
        try:
            if dashboard.active_connections:
                data = await dashboard.get_dashboard_data()
                await dashboard.broadcast_update({
                    "type": "dashboard_update",
                    "data": data
                })
            
            await asyncio.sleep(5)  # Обновления каждые 5 секунд
            
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")
            await asyncio.sleep(10)

@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач"""
    logger.info("🚀 AI Solar 2.0 Admin Dashboard starting...")
    
    # Запускаем периодические обновления
    asyncio.create_task(periodic_updates())
    
    logger.info("✅ Admin Dashboard started successfully")

if __name__ == "__main__":
    uvicorn.run(
        "modern_admin:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )