# backend/admin/routes.py
from fastapi import APIRouter
from core.logging.ai_logger import AILogger

router = APIRouter()
logger = AILogger(db_connection)  # Инициализация подключения к БД

@router.get("/interactions")
async def get_ai_interactions(limit: int = 100):
    """Получает последние AI-взаимодействия"""
    return await logger.db.find().sort("timestamp", -1).limit(limit).to_list()