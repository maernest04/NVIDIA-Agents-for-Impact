from fastapi import FastAPI

from config import settings
from routers import chat, health, resources

app = FastAPI(title=settings.app_name)

app.include_router(health.router)
app.include_router(resources.router)
app.include_router(chat.router)
