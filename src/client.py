# src/client.py
import asyncio, json, sys, websockets

ROOM_ID = sys.argv[1] if len(sys.argv) > 1 else "demo"

async def main():
    uri = f"ws://localhost:8000/ws/{ROOM_ID}"
    async with websockets.connect(uri) as ws:
        me   = None   # "Player1" / "Player2"
        hand = []

        print("サーバー接続。対戦相手を待機中…")

        while True:
            msg = json.loads(await ws.recv())

            # ------------ 初期infoで自分の名前を確定 ------------
            if "info" in msg and msg["info"].startswith("あなたは"):
                me = msg["info"].split()[-2]        # "Player1"/"Player2"
                print(msg["info"])
                continue

            # ------------ ゲーム開始 ----------------------------
            if msg.get("type") == "start":
                hand = msg["hands"][me]
                print("\n=== 対局開始 ===")
                print("手牌:", hand)
                if msg["turn"] == me:
                    print("あなたが先手 → draw を送信")
                    await ws.send(json.dumps({"action": "draw"}))
                continue

            # ------------ 手番通知 ------------------------------
            if msg.get("type") == "turn":
                if msg["turn"] == me:
                    print("\nあなたのターン → draw を送信")
                    await ws.send(json.dumps({"action": "draw"}))
                else:
                    print(f"\n{msg['turn']} のターン待ち")
                continue

            # ------------ あなたがツモ --------------------------
            if msg.get("type") == "draw":
                tile = msg["tile"]; hand = msg["hand"]
                print(f"\n🀄 ツモ: {tile}\n手牌: {hand}")
                discard = int(input("捨てる牌 (数字) → "))
                await ws.send(json.dumps({"action": "discard", "tile": discard}))
                continue

            # ------------ 相手がツモ通知 ------------------------
            if msg.get("type") == "draw_notice":
                print(f"{msg['player']} がツモりました")
                continue

            # ------------ 捨て牌通知 ---------------------------
            if msg.get("type") == "discard":
                who = msg["player"]; tile = msg["tile"]
                print(f"{who} が {tile} を捨てた")
                continue

            # ------------ 終局 -------------------------------
            if msg.get("type") == "end":
                if msg["result"] in ("tsumo", "ron"):
                    print(f"\n🎉 {msg['winner']} の勝利！")
                else:
                    print("\n流局")
                break

            # ------------ エラー / その他 --------------------
            if "error" in msg:
                print("Error:", msg["error"])

if __name__ == "__main__":
    asyncio.run(main())
