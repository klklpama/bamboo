import asyncio
import websockets
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def receive_loop(websocket):
    logger.info("🟢 受信ループ開始")
    try:
        async for message in websocket:
            logger.info(f"← 相手からのメッセージ: {message}")
    except websockets.ConnectionClosed:
        logger.warning("🔌 接続が切れました。")
    except Exception as e:
        logger.error(f"❗ 受信エラー: {e}")

async def input_loop(websocket):
    while True:
        msg = input(">>> メッセージを入力：")
        await websocket.send(msg)
        logger.info("📤 メッセージ送信完了")

async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ サーバーに接続しました")
            # 受信と送信のタスクを並行して実行
            await asyncio.gather(
                receive_loop(websocket),
                input_loop(websocket),
            )
    except Exception as e:
        logger.error(f"❗ 接続エラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())
