import json, logging
from typing import Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.bamboo_core.game import Game, Player

logging.basicConfig(level=logging.DEBUG)   # ← INFO → DEBUG に変更
app = FastAPI()
logger = logging.getLogger(__name__)

rooms: Dict[str, Dict] = {}            # room_id -> {"game": Game, "clients": [ws1,ws2]}
player_ids: Dict[WebSocket, int] = {}  # WebSocket -> 1|2

# ---------- ヘルパ ---------- #
def id2name(pid: int) -> str:
    return f"Player{pid}"

def player_obj(g: Game, pid: int) -> Player:
    return g.players[pid - 1] if isinstance(g.players, list) else g.players[pid]

def turn_name(g: Game) -> str:
    return id2name(current_turn_id(g))

def current_turn_id(g: Game) -> int:
    """Game.current_turn を必ず 1/2 の整数 ID に変換"""
    if isinstance(g.current_turn, int):
        return g.current_turn
    # dict 形式
    if isinstance(g.players, dict):
        for pid, p in g.players.items():
            if g.current_turn is p:
                return pid
    # list 形式
    for idx, p in enumerate(g.players, start=1):
        if g.current_turn is p:
            return idx
    return 0  # 想定外

# ---------- ルート ---------- #
@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo 対戦サーバー起動中！</h1>")

# ---------- WebSocket ---------- #
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

    # 2人揃ったらゲーム生成
    if room["game"] is None and len(room["clients"]) == 2:
        g = room["game"] = Game()
        await broadcast(room, {
            "type": "start",
            "hands": {
                "Player1": sorted(player_obj(g, 1).hand),
                "Player2": sorted(player_obj(g, 2).hand),
            },
            "turn": turn_name(g) # 文字列で送信
        })

    try:
        while True:
            raw = await ws.receive_text()
            logger.debug("%s から受信: %s", id2name(player_ids[ws]), raw) 
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_text(json.dumps({"error": "JSON 形式で送信"})); continue
            await handle(room, ws, msg)
    except WebSocketDisconnect:
        room["clients"].remove(ws); player_ids.pop(ws, None)
        if not room["clients"]:
            rooms.pop(room_id, None)

# ---------- メッセージ処理 ---------- #
async def handle(room, ws, msg):
    g       = room["game"]
    pid     = player_ids[ws]
    pl      = player_obj(g, pid)        # ← Player オブジェクトを取得
    pname   = id2name(pid)
    cur_id  = current_turn_id(g)

    logger.debug("TURN CHECK current_turn=%s pid=%s", cur_id, pid)
    if cur_id != pid:
        await ws.send_text(json.dumps({"error": "まだあなたの手番ではありません"}))
        return

    act = msg.get("action")

    # ---- draw -------------------------------------------------
    if act == "draw":
        tile, win = g.player_draw_and_check_win(pl)          # ★ Player オブジェクト
        if tile is None:
            await broadcast(room, {"type": "end", "result": "draw"}); return

        await ws.send_text(json.dumps({"type": "draw", "tile": tile, "hand": sorted(pl.hand)}))
        await broadcast_others(room, ws, {"type": "draw_notice", "player": pname})

        if win:
            await broadcast(room, {"type": "end", "result": "tsumo", "winner": pname})
        return  # discard 待ち

    # ---- discard ---------------------------------------------
    if act == "discard":
        tile = msg.get("tile")
        try:
            g.discard_tile(pl, tile)                         # ★ Player オブジェクト
        except Exception as e:
            await ws.send_text(json.dumps({"error": str(e)})); return

        win = g.check_win_after_discard(pl)                  # ★ Player オブジェクト
        await broadcast(room, {"type": "discard", "player": pname, "tile": tile})

        if win:
            await broadcast(room, {"type": "end", "result": "ron", "winner": pname}); return

        g.switch_turn()
        await broadcast(room, {"type": "turn", "turn": turn_name(g)})
        return

    await ws.send_text(json.dumps({"error": "未知の action"}))


# ---------- ブロードキャスト ---------- #
async def broadcast(room, data):
    txt = json.dumps(data)
    logger.debug("🛰 broadcast → %s", txt)   # ★ここを追加
    for c in room["clients"]:
        await c.send_text(txt)

async def broadcast_others(room, sender, data):
    txt = json.dumps(data)
    logger.debug("🛰 to‑others → %s", txt)    # ★ここを追加
    for c in room["clients"]:
        if c is not sender:
            await c.send_text(txt)
