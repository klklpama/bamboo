import random
from collections import Counter
from .player import Player

class Game:
    def __init__(self, player1_name="Player1", player2_name="Player2"):
        # ソーズ牌のみ（1〜9を4枚ずつ）
        self.wall = [i for i in range(1, 10)] * 4
        random.shuffle(self.wall)

        # プレイヤー管理：必ず list 構造
        self.players = [
            Player(player1_name),
            Player(player2_name),
        ]

        # 親（最初の手番）は Player1 オブジェクト
        self.current_turn = self.players[0]

        # 各プレイヤーに13枚ずつ配牌
        self.deal_initial_tiles()

    def deal_initial_tiles(self):
        for _ in range(13):
            for p in self.players:
                p.hand.append(self.wall.pop())
        for p in self.players:
            p.hand.sort()

    def draw_tile(self, player: Player) -> int | None:
        if not self.wall:
            return None
        tile = self.wall.pop()
        player.hand.append(tile)
        player.hand.sort()
        return tile

    def check_win(self, player: Player) -> bool:
        counts = Counter(player.hand)
        # 雀頭候補をすべて試す
        for t in range(1, 10):
            if counts[t] >= 2:
                cnt = counts.copy()
                cnt[t] -= 2
                if self._dfs_meld(cnt):
                    return True
        return False

    def _dfs_meld(self, cnt: Counter[int]) -> bool:
        # 残り最小牌を探す
        for t in range(1, 10):
            if cnt[t]:
                break
        else:
            return True  # すべて 0 → 完了

        # 刻子
        if cnt[t] >= 3:
            cnt[t] -= 3
            if self._dfs_meld(cnt): return True
            cnt[t] += 3

        # 順子
        if t <= 7 and cnt[t+1] and cnt[t+2]:
            cnt[t]   -= 1
            cnt[t+1] -= 1
            cnt[t+2] -= 1
            if self._dfs_meld(cnt): return True
            cnt[t]   += 1
            cnt[t+1] += 1
            cnt[t+2] += 1

        return False

    def player_draw_and_check_win(self, player: Player) -> tuple[int | None, bool]:
        tile = self.draw_tile(player)
        if tile is None:
            return None, False
        return tile, self.check_win(player)

    def play_tile(self, player: Player, tile: int) -> None:
        if player is not self.current_turn:
            raise ValueError("あなたのターンではありません！")
        if tile not in player.hand:
            raise ValueError("無効な牌です！")
        player.hand.remove(tile)
        # 捨てたら次の手番にする
        self.switch_turn()

    def discard_tile(self, player: Player, tile: int) -> None:
        # server.py からはこちらを呼び出す
        self.play_tile(player, tile)

    def switch_turn(self) -> None:
        """
        current_turn が Player オブジェクトなら
        └── list の index を見て次を 1|2 の int に、
        int なら 1↔2 を返す、
        をくり返す設計。
        """
        ct = self.current_turn
        # ① もしすでに int なら flip
        if isinstance(ct, int):
            self.current_turn = 2 if ct == 1 else 1
            return

        # ② list 構造のとき
        for idx, p in enumerate(self.players, start=1):
            if p is ct:
                # idx==1 → 次は Player2 → int 2
                # idx==2 → 次は Player1 → int 1
                self.current_turn = 2 if idx == 1 else 1
                return

        raise RuntimeError("switch_turn: current_turn を判定できません")

    def check_win_after_discard(self, player: Player) -> bool:
        # bamboo 麻雀はロンなし
        return False
