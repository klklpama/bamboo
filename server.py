from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import redis.asyncio as redis
import asyncio
import logging
import os
import redis.asyncio as redis


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url, decode_responses=True)

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo server is running (with Redis Pub/Sub)!</h1>")

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    logger.info("✅ Redis 接続完了")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"📡 WebSocket 接続：room_id={room_id}")

    pubsub = redis_client.pubsub()
    await pubsub.subscribe(room_id)

    async def send_to_client():
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await websocket.send_text(message["data"].decode())
        except Exception as e:
            logger.error(f"送信エラー：{e}")

    send_task = asyncio.create_task(send_to_client())

    try:
        while True:
            msg = await websocket.receive_text()
            logger.info(f"📝 受信：{msg}")
            await redis.publish(room_id, msg)
    except WebSocketDisconnect:
        logger.info(f"❌ 切断：{room_id}")
    finally:
        send_task.cancel()
        await pubsub.unsubscribe(room_id)
