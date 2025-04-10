from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import brute_force

app = FastAPI(title="RAR BruteForce")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(brute_force.router, prefix="/api", tags=["brute_force"])

# Подключаем статические файлы
app.mount("/", StaticFiles(directory="app/static", html=True), name="static") 