import json
import logging
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.bamboo_core.game import Game, Player

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# room_id → {"game": Game, "clients": [ws1, ws2]}
rooms: Dict[str, Dict] = {}
# WebSocket → player_id (1 or 2)
player_ids: Dict[WebSocket, int] = {}


def id2name(pid: int) -> str:
    return f"Player{pid}"


def player_obj(g: Game, pid: int) -> Player:
    """dict でも list でも Player オブジェクトを返す"""
    return g.players[pid] if isinstance(g.players, dict) else g.players[pid - 1]


def current_turn_id(g: Game) -> int:
    """g.current_turn を必ず 1/2 の整数に変換"""
    if isinstance(g.current_turn, int):
        return g.current_turn
    if isinstance(g.players, dict):
        for pid, p in g.players.items():
            if p is g.current_turn:
                return pid
    for idx, p in enumerate(g.players, start=1):
        if p is g.current_turn:
            return idx
    raise RuntimeError("Unknown current turn")


def turn_name(g: Game) -> str:
    return id2name(current_turn_id(g))


async def broadcast(room: Dict, data: dict):
    txt = json.dumps(data)
    for ws in room["clients"]:
        await ws.send_text(txt)


async def broadcast_others(room: Dict, sender: WebSocket, data: dict):
    txt = json.dumps(data)
    for ws in room["clients"]:
        if ws is not sender:
            await ws.send_text(txt)


@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 Bamboo 対戦サーバー 起動中</h1>")


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await ws.accept()

    room = rooms.setdefault(room_id, {"game": None, "clients": []})
    if len(room["clients"]) >= 2:
        # すでに満員
        await ws.send_text(json.dumps({"error": "ルームが満員です"}))
        await ws.close()
        return

    pid = len(room["clients"]) + 1
    room["clients"].append(ws)
    player_ids[ws] = pid

    # 個別通知
    await ws.send_text(json.dumps({"info": f"あなたは {id2name(pid)} です"}))

    # 2人揃ったらゲーム開始
    if room["game"] is None and len(room["clients"]) == 2:
        g = room["game"] = Game()
        # start メッセージ
        await broadcast(room, {
            "type": "start",
            "hands": {
                id2name(1): sorted(player_obj(g, 1).hand),
                id2name(2): sorted(player_obj(g, 2).hand),
            },
            "turn": turn_name(g)
        })
        logger.info("▶ start broadcast room=%s", room_id)

    # メッセージ受信ループ
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            await handle(room, ws, msg)
    except WebSocketDisconnect:
        room["clients"].remove(ws)
        player_ids.pop(ws, None)
        # 誰もいなくなったらルーム削除
        if not room["clients"]:
            rooms.pop(room_id, None)
            logger.info("CLOSED room=%s", room_id)


async def handle(room: Dict, ws: WebSocket, msg: dict):
    g   = room["game"]
    pid = player_ids[ws]
    pl  = player_obj(g, pid)
    me  = id2name(pid)

    act = msg.get("action")

    # ---- draw ----
    if act == "draw":
        tile, win = g.player_draw_and_check_win(pl)
        # 山が尽きたら流局
        if tile is None:
            await broadcast(room, {"type": "end", "result": "draw"})
            return

        # ツモ通知 (本人向け)
        await ws.send_text(json.dumps({
            "type": "draw",
            "tile": tile,
            "hand": sorted(pl.hand)
        }))
        # 他プレイヤーへツモ通知
        await broadcast_others(room, ws, {
            "type": "draw_notice", "player": me
        })

        # ツモのあと自動手番切替
        g.switch_turn()
        await broadcast(room, {"type": "turn", "turn": turn_name(g)})

        # ツモ上がりなら終局通知
        if win:
            await broadcast(room, {
                "type": "end", "result": "tsumo", "winner": me
            })
        return

    # ---- discard ----
    if act == "discard":
        tile = msg.get("tile")
        try:
            g.discard_tile(pl, tile)
        except Exception as e:
            await ws.send_text(json.dumps({"error": str(e)}))
            return

        # 捨て牌通知
        await broadcast(room, {"type": "discard", "player": me, "tile": tile})

        # ロン上がりチェック
        if g.check_win_after_discard(pl):
            await broadcast(room, {
                "type": "end", "result": "ron", "winner": me
            })
            return

        # 通常手番切替
        g.switch_turn()
        await broadcast(room, {"type": "turn", "turn": turn_name(g)})
        return

    # unknown action
    await ws.send_text(json.dumps({"error": "未知の action"}))
