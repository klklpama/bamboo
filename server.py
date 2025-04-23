from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running!</h1>")

# ルームごとにクライアントを管理する辞書
connected_rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"📡 WebSocket 接続: ルームID = {room_id}")

    # ルームが存在しない場合は新規作成
    if room_id not in connected_rooms:
        connected_rooms[room_id] = []
    connected_rooms[room_id].append(websocket)

    try:
        while True:
            # クライアントからのメッセージを受信
            data = await websocket.receive_text()
            logger.info(f"[{room_id}] 受信: {data}")

            # 同じルーム内の他のクライアントにメッセージを送信
            for client in connected_rooms[room_id]:
                if client != websocket:
                    try:
                        await client.send_text(f"誰か：{data}")
                    except Exception as e:
                        logger.warning(f"送信エラー: {e}")
    except WebSocketDisconnect:
        # クライアントの切断処理
        connected_rooms[room_id].remove(websocket)
        logger.info(f"❌ 切断: ルームID = {room_id}")
