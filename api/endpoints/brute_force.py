from fastapi import APIRouter, UploadFile, File, Form, Query
from typing import Optional, List
import os
import tempfile
from app.worker import bruteforce_rar

router = APIRouter()

@router.post("/upload-and-bruteforce/")
async def upload_and_bruteforce(
    file: UploadFile = File(...),
    min_length: int = Form(4),
    max_length: int = Form(8),
    charset: Optional[str] = Form(None),
    max_attempts: Optional[int] = Form(None)
):
    # Проверяем расширение файла
    if not file.filename.endswith('.rar'):
        return {"error": "Файл должен быть в формате RAR"}
    
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.rar') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    # Запускаем задачу перебора
    task = bruteforce_rar.delay(
        temp_path,
        min_length=min_length,
        max_length=max_length,
        charset=charset,
        max_attempts=max_attempts
    )
    
    return {"task_id": task.id}

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    task = bruteforce_rar.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'status': task.state,
            'info': None
        }
    elif task.state == 'PROGRESS':
        response = {
            'status': task.state,
            'info': task.info
        }
    elif task.state == 'SUCCESS':
        response = {
            'status': task.state,
            'result': task.result
        }
    else:
        response = {
            'status': task.state,
            'error': str(task.info)
        }
    return response

@router.get("/charsets")
async def get_charsets():
    return {
        "charsets": [
            {"name": "Все печатные символы", "value": ""},
            {"name": "Строчные буквы (a-z)", "value": "abcdefghijklmnopqrstuvwxyz"},
            {"name": "Заглавные буквы (A-Z)", "value": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"},
            {"name": "Буквы (a-z, A-Z)", "value": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"},
            {"name": "Цифры (0-9)", "value": "0123456789"},
            {"name": "Буквы и цифры", "value": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"},
            {"name": "Специальные символы", "value": "!@#$%^&*()_+-=[]{}|;:,.<>?"}
        ]
    } 