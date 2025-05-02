# bamboo_cli.py
from src.bamboo_core.game import Game

def show_hand(player, drawn=None):
    """手牌を数字だけで表示。drawn を * でマーク"""
    out = []
    used_mark = False
    for t in player.hand:
        if drawn is not None and t == drawn and not used_mark:
            out.append(f"*{t}")
            used_mark = True            # 1 枚だけ * を付ける
        else:
            out.append(f" {t}")
    print("hand:", " ".join(out))

def input_discard(player):
    while True:
        raw = input(f"[{player.name}] 捨てる牌の数字 (1‑9) → ").strip()
        if raw.isdigit():
            tile = int(raw)
            if tile in player.hand:
                return tile
        print("手牌に無いか入力不正です。")

def main():
    game = Game("Player1", "Player2")

    while not game.is_game_over():
        pl = game.current_turn
        print(f"\n=== {pl.name} のターン ===")
        show_hand(pl)

        # ツモ
        tile, is_win = game.player_draw_and_check_win(pl)
        if tile is None:
            print("山切れ → 流局")
            break
        print(f"ツモ牌: {tile}")
        show_hand(pl, drawn=tile)

        if is_win:
            print(f"🎉 {pl.name} ツモ和了！")
            break

        # 捨てる
        discard = input_discard(pl)
        try:
            game.play_tile(pl, discard)
        except ValueError as e:
            print(e)
            continue

        if game.check_win_after_discard(pl):
            print(f"🎉 {pl.name} 和了！（捨て牌後）")
            break

        print(f"山牌残り: {game.get_wall_count()}")

    print("\nゲーム終了")

if __name__ == "__main__":
    main()
