# main.py
from email.mime import base
from fastapi import FastAPI
from auth import router as auth_router
from routes.upload_protocol import router as file_router
from routes.chat import router as chat_router

app = FastAPI(root_path="/api")

app.include_router(auth_router, prefix="/auth")
app.include_router(file_router, prefix="/protocol-assistant")
app.include_router(chat_router, prefix="/protocol-assistant")

