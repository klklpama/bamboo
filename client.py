import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

async def receive_loop(websocket):
    logger.info("🟢 受信ループ開始")
    try:
        while True:
            data = await websocket.recv()
            logger.info(f"← 相手からのメッセージ：{data}")
    except websockets.ConnectionClosed:
        logger.warning("🔌 接続が切れました。")
    except Exception as e:
        logger.error(f"❗ 受信エラー：{e}")

async def input_loop(websocket):
    loop = asyncio.get_running_loop()
    while True:
        msg = await loop.run_in_executor(None, input, ">>> メッセージを入力：")
        await websocket.send(msg)
        logger.info("📤 メッセージ送信完了")

async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"
    async with websockets.connect(uri) as websocket:
        logger.info("✅ サーバーに接続しました")
        await asyncio.gather(
            receive_loop(websocket),
            input_loop(websocket),
        )

if __name__ == "__main__":
    asyncio.run(main())
