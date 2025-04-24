import asyncio
import websockets
import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ANSIカラーコード
# 活きていないので今後見直し
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

async def receive_loop(websocket):
    logging.info("🟢 受信ループ開始")
    try:
        while True:
            data = await websocket.recv()
            if "誰か：" in data:
                # 相手からのメッセージ（緑）
                print(f"{GREEN}← {data}{RESET}")
            else:
                # 自分のメッセージ（赤）
                print(f"{RED}← {data} (you){RESET}")
    except websockets.ConnectionClosed:
        logging.warning("🔌 接続が切れました。")
    except Exception as e:
        logging.error(f"❗ 受信エラー：{e}")

async def input_loop(websocket):
    while True:
        msg = input(">>> メッセージを入力：")
        await websocket.send(msg)
        logging.info("📤 メッセージ送信完了")

async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"
    async with websockets.connect(uri) as websocket:
        logging.info("✅ サーバーに接続しました")
        await asyncio.gather(
            receive_loop(websocket),
            input_loop(websocket),
        )

if __name__ == "__main__":
    asyncio.run(main())
