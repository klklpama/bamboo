from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# Web画面用ルート
@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running!</h1>")

# 各ルームごとのクライアント管理
connected_clients = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    # ルームがなければ作る
    if room_id not in connected_clients:
        connected_clients[room_id] = []

    connected_clients[room_id].append(websocket)
    print(f"🧑‍🤝‍🧑 接続: room = {room_id}, 現在の人数 = {len(connected_clients[room_id])}")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"💬 受信 ({room_id}): {data}")

            # 同じルームの他のクライアントにブロードキャスト
            for client in connected_clients[room_id][:]:
                if client != websocket:
                    try:
                        await client.send_text(f"{room_id}内の誰か：{data}")
                    except:
                        connected_clients[room_id].remove(client)
    except WebSocketDisconnect:
        connected_clients[room_id].remove(websocket)
        print(f"❌ 切断: room = {room_id}, 残り = {len(connected_clients[room_id])}")
        # ルームが空になったら削除
        if not connected_clients[room_id]:
            del connected_clients[room_id]
