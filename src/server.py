from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from bamboo_core.game import Game
import logging
import asyncio

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ゲームインスタンスと接続管理
games = {}  # ルームID → Gameインスタンス
clients = {}  # ルームID → [WebSocket, WebSocket]
player_ids = {}  # WebSocket → player_id

@app.get("/")
async def root():
    return HTMLResponse("<h1>🀄 bamboo 対戦サーバー起動中！</h1>")

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"📡 接続: {room_id}")

    if room_id not in games:
        games[room_id] = Game()
        clients[room_id] = []

    if len(clients[room_id]) >= 2:
        await websocket.send_text("ルームが満員です。")
        await websocket.close()
        return

    player_id = len(clients[room_id]) + 1
    clients[room_id].append(websocket)
    player_ids[websocket] = player_id

    await websocket.send_text(f"あなたはプレイヤー {player_id} です。")
    await send_hand(websocket, room_id, player_id)  # 配牌表示

    try:
        while True:
            msg = await websocket.receive_text()
            logger.info(f"[{room_id}] P{player_id}：{msg}")

            game = games[room_id]

            if game.current_turn != player_id:
                await websocket.send_text("まだあなたのターンではありません。")
                continue

            try:
                discard_tile = int(msg.strip())  # strip対策
                game.discard_tile(player_id, discard_tile)
            except Exception as e:
                await websocket.send_text(f"❌ エラー：{e}")
                continue

            await broadcast(room_id, f"📝 プレイヤー{player_id}が「{discard_tile}」を捨てました")
            game.switch_turn()

            # 次のプレイヤーの処理
            next_player = game.current_turn
            tile, is_win = game.player_draw_and_check_win(next_player)
            next_ws = clients[room_id][next_player - 1]

            if tile is None:
                await broadcast(room_id, "🃏 山札が尽きました。引き分けです。")
                break

            await next_ws.send_text(f"🀄 1枚引きました: {tile}")
            await send_hand(next_ws, room_id, next_player)  # ツモ後表示

            if is_win:
                await broadcast(room_id, f"🎉 プレイヤー {next_player} の勝利！")
                break

    except WebSocketDisconnect:
        logger.info(f"❌ 切断: P{player_id} / {room_id}")
        clients[room_id].remove(websocket)
        del player_ids[websocket]

# 🔄 手札を送信
async def send_hand(ws, room_id, player_id):
    hand = games[room_id].get_hand(player_id)
    await ws.send_text(f"🀄 あなたの手札: {sorted(hand)}")

# 📢 ルーム内全員に送信
async def broadcast(room_id, message):
    for ws in clients[room_id]:
        await ws.send_text(message)
