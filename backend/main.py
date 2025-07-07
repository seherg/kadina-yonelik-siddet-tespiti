# backend/main.py

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from backend.websocket_handler import handle_websocket
import uvicorn
import os
from backend.database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()
# ✅ frontend klasörünü /static olarak sunuyoruz
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def get_index():
    return FileResponse(os.path.join("frontend", "index.html"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await handle_websocket(websocket)
    except WebSocketDisconnect:
        print("🔌 WebSocket bağlantısı kesildi.")


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
