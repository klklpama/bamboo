import asyncio
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

# 🟢 受信ループ（手札が来たら表示）
async def receive_loop(websocket, player_id):
    logger.info("🟢 受信ループ開始")
    try:
        while True:
            data = await websocket.recv()
            if data.startswith("あなたの手札:"):
                print(f"🀄 あなたの手札：{data.replace('あなたの手札:', '').strip()}")
            else:
                logger.info(f"← 相手からのメッセージ：{data}")
    except websockets.ConnectionClosed:
        logger.warning("🔌 接続が切れました。")
    except Exception as e:
        logger.error(f"❗ 受信エラー：{e}")

# 💬 入力ループ（捨てる牌を送信）
async def input_loop(websocket, player_id):
    loop = asyncio.get_running_loop()
    while True:
        raw_msg = await loop.run_in_executor(None, input, "🀄 手札から1枚選んで捨ててください：")
        try:
            msg = str(int(raw_msg.strip()))  # 必ず数値形式にする
            await websocket.send(msg)
            logger.info("📤 送信完了")
        except ValueError:
            logger.warning("⚠️ 数字を入力してください")

# 🚀 メイン
async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    player_id = int(input("👤 プレイヤー番号を入力（1 or 2）：").strip())

    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("✅ サーバーに接続しました")
            await asyncio.gather(
                receive_loop(websocket, player_id),
                input_loop(websocket, player_id)
            )
    except Exception as e:
        logger.error(f"🚨 接続エラー：{e}")

if __name__ == "__main__":
    asyncio.run(main())
