# core/logging/ai_logger.py
from datetime import datetime
from pydantic import BaseModel

class AIInteraction(BaseModel):
    user_id: str
    query: str
    ai_provider: str  # "dashka", "claude", "deepseek"
    response: str
    timestamp: datetime = datetime.now()
    metadata: dict  # {tokens_used: 120, confidence: 0.95}

class AILogger:
    def __init__(self, db_connection):
        self.db = db_connection

    async def log_interaction(self, interaction: AIInteraction):
        """Сохраняет взаимодействие в БД"""
        await self.db.insert_one(interaction.dict())