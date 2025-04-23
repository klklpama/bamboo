import asyncio
import websockets

async def receive_loop(websocket):
    print("🟢 受信ループ開始")
    try:
        while True:
            data = await websocket.recv()
            print(f"← 相手からのメッセージ：{data}")
    except websockets.ConnectionClosed:
        print("🔌 接続が切れました。")
    except Exception as e:
        print(f"❗ 受信エラー：{e}")

async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"

    async with websockets.connect(uri) as websocket:
        print("✅ 接続しました！")

        # ✅ 入力と受信を完全に並行で処理
        async def input_loop():
            while True:
                msg = input(">>> メッセージを入力：")
                await websocket.send(msg)
                print("📤 送信完了！")

        await asyncio.gather(
            receive_loop(websocket),
            input_loop(),
        )

if __name__ == "__main__":
    asyncio.run(main())
