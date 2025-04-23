import asyncio
import websockets

async def receive_loop(websocket):
    print("🟢 受信ループ開始")
    try:
        async for data in websocket:
            print(f"← 相手からのメッセージ：{data}")
    except websockets.ConnectionClosed:
        print("🔌 接続が切れました。")
    except Exception as e:
        print(f"❗ 受信エラー：{e}")

async def input_loop(websocket):
    while True:
        msg = input(">>> メッセージを入力：")
        await websocket.send(msg)
        print("📤 送信完了！")

async def main():
    room_id = input("🎮 ルームIDを入力してください：").strip()
    uri = f"wss://bamboo-kl8a.onrender.com/ws/{room_id}"
    async with websockets.connect(uri) as websocket:
        print("✅ 接続しました！")

        # 🎯 並列で安全に送受信するには、Taskを別にして明示的に分離
        receive_task = asyncio.create_task(receive_loop(websocket))
        input_task = asyncio.create_task(input_loop(websocket))

        await asyncio.wait(
            [receive_task, input_task],
            return_when=asyncio.FIRST_COMPLETED
        )

if __name__ == "__main__":
    asyncio.run(main())
