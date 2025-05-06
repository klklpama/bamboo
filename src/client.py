#!/usr/bin/env python3
# ======================================================================
#  bamboo_cli  –  Text-based client for the 2-player “bamboo” mah-jong app
# ======================================================================
import asyncio
import json
import sys
from concurrent.futures import ThreadPoolExecutor

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

SERVER = "ws://127.0.0.1:8000/ws/{}"
ROOM   = sys.argv[1] if len(sys.argv) > 1 else "demo"

# ────────────────────────── 非同期 input() ────────────────────────────
executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="input")
async def ainput(prompt: str = "") -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, lambda: input(prompt).strip())

# ────────────────────────── 表示ユーティリティ ──────────────────────────
def show_hand(hand: list[int]) -> None:
    print("手牌:", hand)

def show_draw(tile: int, hand: list[int]) -> None:
    print(f"\n🀄 ツモ: {tile}")
    show_hand(hand)

def translate(msg: dict) -> None:
    kind = msg.get("type")
    if kind == "draw_notice":
        print(f"{msg['player']} がツモりました")
    elif kind == "discard":
        print(f"{msg['player']} が {msg['tile']} を捨てた")

# ────────────────────────────── メイン ──────────────────────────────
async def main() -> None:
    url = SERVER.format(ROOM)
    async with websockets.connect(url) as ws:

        # ── 初期メッセージ(info / start) を順不同で取得 ──────────────
        my_name: str | None = None
        start:   dict | None = None
        while not (my_name and start):
            raw = await ws.recv()
            try:
                init_msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if "info" in init_msg:
                # 例: "あなたは Player1 です"
                parts   = init_msg["info"].split()
                my_name = parts[-2]
            elif init_msg.get("type") == "start":
                start = init_msg

        hand    = start["hands"][my_name]
        my_turn = (start["turn"] == my_name)

        print(f"\nあなたは {my_name} です")
        print("\n=== 対局開始 ===")
        show_hand(hand)

        # 以降のメッセージ受信用タスク
        recv_task = asyncio.create_task(ws.recv())

        # ── メインループ ─────────────────────────────────────────
        while True:
            # ── 自分のターン ───────────────────────────────────
            if my_turn:
                # 既存 recv をキャンセルしてから進行
                recv_task.cancel()
                await asyncio.gather(recv_task, return_exceptions=True)

                # ツモ
                await ws.send(json.dumps({"action": "draw"}))
                draw_msg = json.loads(await ws.recv())
                show_draw(draw_msg["tile"], draw_msg["hand"])
                hand = draw_msg["hand"]

                # ツモ和了チェック (win フラグ)
                if draw_msg.get("win"):
                    my_turn   = False
                    recv_task = asyncio.create_task(ws.recv())
                    continue

                # 捨て牌
                while True:
                    tile_str = await ainput("捨てる牌 (数字) → ")
                    if tile_str.isdigit():
                        await ws.send(json.dumps({
                            "action": "discard",
                            "tile": int(tile_str)
                        }))
                        break
                    print("❌ 数字で入力してください")

                my_turn   = False
                recv_task = asyncio.create_task(ws.recv())
                continue

            # ── 相手の行動待ち ─────────────────────────────────
            done, _ = await asyncio.wait([recv_task],
                                         return_when=asyncio.FIRST_COMPLETED)

            if recv_task in done:
                raw = recv_task.result()
                # ── JSON パース ──────────────────────────────
                try:
                    msg = json.loads(raw)
                except json.JSONDecodeError:
                    recv_task = asyncio.create_task(ws.recv())
                    continue

                # ── type がない場合はスキップ ────────────────────
                mtype = msg.get("type")
                if mtype is None:
                    recv_task = asyncio.create_task(ws.recv())
                    continue

                # ── 手番交代通知 ──────────────────────────────
                if mtype == "turn":
                    my_turn = (msg["turn"] == my_name)

                # ── ツモ/捨て牌通知 ───────────────────────────
                elif mtype in {"draw_notice", "discard"}:
                    translate(msg)

                # ── 終局通知 ─────────────────────────────────
                elif mtype == "end":
                    result = msg["result"]
                    if result == "draw":
                        print("\n🀄 流局！山札が尽きました")
                    else:
                        who  = "あなた" if msg["winner"] == my_name else msg["winner"]
                        yaku = "ツモ" if result == "tsumo" else "ロン"
                        print(f"\n🎉 {who} の{yaku}和了！")
                    break

                # 次のメッセージ受信用タスクを再作成
                recv_task = asyncio.create_task(ws.recv())

        # ── 終局クリーンアップ ─────────────────────────────────
        recv_task.cancel()
        await asyncio.gather(recv_task, return_exceptions=True)
        executor.shutdown(cancel_futures=True)
        await ws.close()
        print("\n対局終了。お疲れさまでした！")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹   手動終了しました")
