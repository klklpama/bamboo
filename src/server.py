# src/server.py  ── bamboo 対戦サーバー（Playerオブジェクト統一版）
import json, logging
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.bamboo_core.game import Game, Player  # Game.players は {1: Player, 2: Player}

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rooms: Dict[str, Dict] = {}            # room_id -> {"game": Game, "clients": [ws1,ws2]}
player_ids: Dict[WebSocket, int] = {}  # WebSocket -> 1|2


# ───────── 便利ヘルパ ─────────
def id2name(pid: int) -> str: return f"Player{pid}"          # 1 -> "Player1"
def player_obj(g: Game, pid: int) -> Player:
    """Game.players が list でも dict でも Player を返す"""
    return g.players[pid - 1] if isinstance(g.players, list) else g.players[pid]


# ───────── ルート ─────────
@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo 対戦サーバー起動中！</h1>")


# ───────── WebSocket ─────────
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await ws.accept()

    room = rooms.setdefault(room_id, {"game": None, "clients": []})
    if len(room["clients"]) >= 2:
        await ws.send_text(json.dumps({"error": "ルームが満員です"}))
        await ws.close(); return

    pid = len(room["clients"]) + 1
    room["clients"].append(ws); player_ids[ws] = pid
    await ws.send_text(json.dumps({"info": f"あなたは {id2name(pid)} です"}))

    # 2人揃ったらゲーム生成 & 配牌
    if room["game"] is None and len(room["clients"]) == 2:
        g = room["game"] = Game()
        await broadcast(room, {
            "type": "start",
            "hands": {
                "Player1": sorted(player_obj(g, 1).hand),
                "Player2": sorted(player_obj(g, 2).hand),
            },
            "turn": id2name(g.current_turn)
        })
        await broadcast(room, {"type": "turn", "turn": id2name(g.current_turn)})

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "JSON 形式で送信してください"})); continue
            await handle(room, ws, msg)
    except WebSocketDisconnect:
        room["clients"].remove(ws); player_ids.pop(ws, None)
        if not room["clients"]:
            rooms.pop(room_id, None)


# ───────── メッセージ処理 ─────────
async def handle(room, ws, msg):
    g: Game = room["game"]
    pid     = player_ids[ws]

# ---------- ブロードキャスト ---------------------------------------------
async def broadcast(room, data):
    txt = json.dumps(data)
    for c in room["clients"]:
        await c.send_text(txt)

async def broadcast_others(room, sender, data):
    txt = json.dumps(data)
    for c in room["clients"]:
        if c is not sender:
            await c.send_text(txt)
