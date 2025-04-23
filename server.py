from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()  # ✅ まず app を定義

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running!</h1>")

connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"受信：{data}")
            for client in connected_clients[:]:
                try:
                    await client.send_text(f"誰か：{data}")
                except:
                    connected_clients.remove(client)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
