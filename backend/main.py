from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from . import models, schemas
from .database import SessionLocal, engine

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

# Создаем FastAPI приложение
app = FastAPI(
    title="AI Solar 2.0 API",
    description="API for AI task coordination system",
    version="2.0.0"
)

# Dependency для получения БД сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "AI Solar 2.0 API",
        "version": "2.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Solar 2.0 API"
    }

@app.get("/tasks")
def list_tasks(
    chat_id: Optional[int] = Query(None, description="Filter by Telegram chat ID"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100, description="Limit number of results"),
    db: Session = Depends(get_db)
):
    """Получить список задач с фильтрацией"""
    try:
        query = db.query(models.Task)
        
        # Применяем фильтры
        if chat_id:
            query = query.filter(models.Task.telegram_chat_id == chat_id)
        if assignee:
            query = query.filter(models.Task.assignee == assignee)
        if status:
            query = query.filter(models.Task.status == status)
            
        # Сортируем по дате создания (новые первыми)
        tasks = query.order_by(models.Task.created_at.desc()).limit(limit).all()
        
        return {"tasks": tasks}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")

@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Создать новую задачу"""
    try:
        # Создаем новую задачу
        db_task = models.Task(
            id=str(uuid.uuid4()),
            assignee=task.assignee,
            title=task.title,
            description=task.description,
            status="pending",
            telegram_chat_id=task.telegram_chat_id,
            created_by=task.created_by,
            input_data=task.input_data,
            created_at=datetime.utcnow()
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return {
            "id": db_task.id,
            "status": "created",
            "message": f"Task assigned to {task.assignee}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.get("/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Получить задачу по ID"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")

@app.put("/tasks/{task_id}")
def update_task(
    task_id: str, 
    task_update: schemas.TaskUpdate, 
    db: Session = Depends(get_db)
):
    """Обновить задачу"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Обновляем поля
        if task_update.status:
            task.status = task_update.status
        if task_update.output_data:
            task.output_data = task_update.output_data
        if task_update.title:
            task.title = task_update.title
            
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task_id,
            "status": "updated",
            "message": "Task updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")

@app.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: str,
    completion_data: schemas.TaskCompletion,
    db: Session = Depends(get_db)
):
    """Завершить задачу с результатом"""
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
            
        task.status = "completed"
        task.output_data = completion_data.output_data
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task_id,
            "status": "completed",
            "message": "Task completed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error completing task: {str(e)}")

@app.get("/stats")
def get_statistics(db: Session = Depends(get_db)):
    """Получить статистику системы"""
    try:
        # Общая статистика
        total_tasks = db.query(models.Task).count()
        pending_tasks = db.query(models.Task).filter(models.Task.status == "pending").count()
        in_progress_tasks = db.query(models.Task).filter(models.Task.status == "in_progress").count()
        completed_tasks = db.query(models.Task).filter(models.Task.status == "completed").count()
        
        # Статистика по агентам
        claude_tasks = db.query(models.Task).filter(models.Task.assignee == "claude").count()
        deepseek_tasks = db.query(models.Task).filter(models.Task.assignee == "deepseek").count()
        grok_tasks = db.query(models.Task).filter(models.Task.assignee == "grok").count()
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "claude_tasks": claude_tasks,
            "deepseek_tasks": deepseek_tasks,
            "grok_tasks": grok_tasks,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

# Claude Integration Endpoints
@app.get("/claude/pending")
def get_claude_pending_tasks(db: Session = Depends(get_db)):
    """Получить ожидающие задачи для Claude"""
    try:
        tasks = db.query(models.Task).filter(
            models.Task.assignee == "claude",
            models.Task.status == "pending"
        ).order_by(models.Task.created_at.asc()).all()
        
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Claude tasks: {str(e)}")

@app.post("/claude/submit/{task_id}")
def submit_claude_response(
    task_id: str,
    response_data: schemas.ClaudeResponse,
    db: Session = Depends(get_db)
):
    """Отправить ответ Claude для задачи"""
    try:
        task = db.query(models.Task).filter(
            models.Task.id == task_id,
            models.Task.assignee == "claude"
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Claude task not found")
            
        task.status = "completed"
        task.output_data = {
            "claude_response": response_data.response,
            "analysis_type": response_data.analysis_type,
            "recommendations": response_data.recommendations,
            "completed_by": "claude"
        }
        task.completed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(task)
        
        return {
            "id": task_id,
            "status": "claude_response_submitted",
            "message": "Claude response submitted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error submitting Claude response: {str(e)}")

# DeepSeek Integration Endpoints
@app.get("/deepseek/pending")
def get_deepseek_pending_tasks(db: Session = Depends(get_db)):
    """Получить ожидающие задачи для DeepSeek"""
    try:
        tasks = db.query(models.Task).filter(
            models.Task.assignee == "deepseek",
            models.Task.status == "pending"
        ).order_by(models.Task.created_at.asc()).all()
        
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving DeepSeek tasks: {str(e)}")

# Grok Integration Endpoints  
@app.get("/grok/pending")
def get_grok_pending_tasks(db: Session = Depends(get_db)):
    """Получить ожидающие задачи для Grok"""
    try:
        tasks = db.query(models.Task).filter(
            models.Task.assignee == "grok",
            models.Task.status == "pending"
        ).order_by(models.Task.created_at.asc()).all()
        
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Grok tasks: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Resource not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "status_code": 500}