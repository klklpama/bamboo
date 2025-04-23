from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running!</h1>")

# 🔑 ルームごとにクライアントを管理
connected_rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"📡 WebSocket 接続されたよ！ルームID: {room_id}")

    if room_id not in connected_rooms:
        connected_rooms[room_id] = []
    connected_rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"[{room_id}] 受信：{data}")
            
            # ✅ 送信者と受信者でメッセージを分けて送信
            for client in connected_rooms[room_id][:]:
                try:
                    if client == websocket:
                        await client.send_text(f"🟢 あなた：{data}")
                    else:
                        await client.send_text(f"🔵 相手：{data}")
                except:
                    connected_rooms[room_id].remove(client)
    except WebSocketDisconnect:
        logger.info(f"❌ 切断：{room_id}")
        connected_rooms[room_id].remove(websocket)
