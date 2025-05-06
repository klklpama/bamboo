import json, logging
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.bamboo_core.game import Game, Player

app = FastAPI()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# room_id → {"game": Game, "clients": [WebSocket, ...]}
rooms: Dict[str, Dict] = {}
# WebSocket → player id (1 or 2)
player_ids: Dict[WebSocket, int] = {}

MAX_PLAYERS = 2

def id2name(pid: int) -> str:
    return f"Player{pid}"

def player_obj(g: Game, pid: int) -> Player:
    # Game.players は list なので pid-1 で取得
    return g.players[pid - 1]

def turn_name(g: Game) -> str:
    ct = g.current_turn
    if isinstance(ct, int):
        return id2name(ct)
    if isinstance(ct, Player):
        return ct.name
    # 万が一の fallback
    return str(ct)

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
    return HTMLResponse("<h1>🀄 bamboo 対戦サーバー 起動中！</h1>")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    await ws.accept()
    logger.debug("WS open room=%s", room_id)

    room = rooms.setdefault(room_id, {"game": None, "clients": []})
    if len(room["clients"]) >= MAX_PLAYERS:
        await ws.send_text(json.dumps({"error": "満員です"}))
        await ws.close()
        return

    pid = len(room["clients"]) + 1
    room["clients"].append(ws)
    player_ids[ws] = pid

    # 個別通知
    await ws.send_text(json.dumps({"info": f"あなたは {id2name(pid)} です"}))

    # ２人揃ったら start
    if room["game"] is None and len(room["clients"]) == MAX_PLAYERS:
        g = Game()
        room["game"] = g
        await broadcast(room, {
            "type": "start",
            "hands": {
                "Player1": sorted(g.players[0].hand),
                "Player2": sorted(g.players[1].hand),
            },
            "turn": turn_name(g)
        })
        logger.info("▶ start broadcast room=%s", room_id)

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            await handle(room, ws, msg)
    except WebSocketDisconnect:
        room["clients"].remove(ws)
        player_ids.pop(ws, None)
        if not room["clients"]:
            rooms.pop(room_id)
            logger.info("✖ closed room=%s", room_id)

async def handle(room: Dict, ws: WebSocket, msg: dict):
    g: Game = room["game"]
    pid      = player_ids[ws]
    pl       = player_obj(g, pid)
    me       = id2name(pid)
    act      = msg.get("action")

    logger.debug("🔄 handle start: current_turn=%s pid=%d", turn_name(g), pid)

    # ── ツモ
    if act == "draw":
        tile, win = g.player_draw_and_check_win(pl)
        if tile is None:
            # 流局
            await broadcast(room, {"type": "end", "result": "draw"})
            return

        # (1) ツモ結果を自分に
        await ws.send_text(json.dumps({
            "type": "draw",
            "tile": tile,
            "hand": sorted(pl.hand)
        }))
        # (2) 相手にツモ通知だけ
        await broadcast_others(room, ws, {
            "type": "draw_notice",
            "player": me
        })

        # ツモ和了
        if win:
            await broadcast(room, {
                "type": "end",
                "result": "tsumo",
                "winner": me
            })
        return

    # ── 捨て牌
    if act == "discard":
        tile = msg.get("tile")
        try:
            g.discard_tile(pl, tile)  # play_tile → switch_turn まで呼ばれる
        except Exception as e:
            await ws.send_text(json.dumps({"error": str(e)}))
            return

        # 捨て牌を全員に通知
        await broadcast(room, {
            "type": "discard",
            "player": me,
            "tile": tile
        })

        # ロン（常に False）
        if g.check_win_after_discard(pl):
            await broadcast(room, {
                "type": "end",
                "result": "ron",
                "winner": me
            })
            return

        # 捨て牌後に手番が switch_turn 済 → turn 通知
        await broadcast(room, {
            "type": "turn",
            "turn": turn_name(g)
        })
        return

    # ── 不明
    await ws.send_text(json.dumps({"error": "unknown action"}))
