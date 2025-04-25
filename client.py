import asyncio
import websockets
import logging
from bamboo_core.game import Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("client")

game = Game()  # ゲームオブジェクトをグローバルに作成

# 🟢 受信ループ
async def receive_loop(websocket, player_id):
    logger.info("🟢 受信ループ開始")
    try:
        while True:
            message = await websocket.recv()
            logger.info(f"← 相手からのメッセージ：{message}")
            # 受け取ったメッセージを Game に渡して処理（仮）
            game.handle_message(message, player_id)
    except websockets.ConnectionClosed:
        logger.warning("🔌 接続が切れました。")
    except Exception as e:
        logger.error(f"❗ エラー：{e}")

# 💬 入力ループ（自分のターン時のみ）
async def input_loop(websocket, player_id):
    loop = asyncio.get_running_loop()
    while True:
        if not game.is_my_turn(player_id):
            await asyncio.sleep(0.1)
            continue
        card = await loop.run_in_executor(None, input, "🀄 手札から1枚選んで捨ててください：")
        await websocket.send(card)
        logger.info("📤 送信完了")
        game.end_turn(player_id)

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
