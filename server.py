from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running!</h1>")

# 🔑 ルームごとにクライアントを管理
connected_rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    print(f"📡 WebSocket 接続されたよ！ルームID: {room_id}")

    if room_id not in connected_rooms:
        connected_rooms[room_id] = []
    connected_rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"[{room_id}] 受信：{data}")
            for client in connected_rooms[room_id][:]:
                try:
                    await client.send_text(f"誰か：{data}")
                except:
                    connected_rooms[room_id].remove(client)
    except WebSocketDisconnect:
        print(f"❌ 切断：{room_id}")
        connected_rooms[room_id].remove(websocket)
