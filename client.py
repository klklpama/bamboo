import asyncio
import websockets

async def receive_loop(websocket):
    print("🟢 receive_loop 開始")
    while True:
        try:
            data = await websocket.recv()
            print(f"← 相手からのメッセージ：{data}")
        except websockets.ConnectionClosed:
            print("🔌 接続が切れました。")
            break
        except Exception as e:
            print(f"❗ 受信エラー：{e}")
            break

async def main():
    uri = "wss://bamboo-kl8a.onrender.com/ws"  # ✅ Renderに接続
    async with websockets.connect(uri) as websocket:
        print("✅ 接続しました！")
        asyncio.create_task(receive_loop(websocket))
        while True:
            msg = input(">>> メッセージを入力：")
            await websocket.send(msg)
            print("送信完了！")

if __name__ == "__main__":
    asyncio.run(main())
