import random
from .player import Player
from collections import Counter


class Game:
    def __init__(self, player1_name="Player1", player2_name="Player2"):
        # ソーズ牌のみ（1〜9を4枚ずつ）
        self.wall = [i for i in range(1, 10)] * 4
        random.shuffle(self.wall)

        # プレイヤー管理
        self.players = [
            Player(player1_name),
            Player(player2_name),
        ]

        # 親設定（Player1を親に設定）
        self.current_turn = self.players[0]

        # 各プレイヤーに13枚ずつ配牌
        self.deal_initial_tiles()

    def deal_initial_tiles(self):
        for _ in range(13):
            for player in self.players:
                player.hand.append(self.wall.pop())
        for player in self.players:
            player.hand.sort()

    def get_hand(self, player):
        return player.hand

    def play_tile(self, player, tile):
        if player != self.current_turn:
            raise ValueError("あなたのターンではありません！")
        if tile not in player.hand:
            raise ValueError("無効な牌です！")
        player.hand.remove(tile)
        print(f"{player.name} が {tile} を捨てました")
        self.switch_turn()

    def draw_tile(self, player):
        if not self.wall:
            print("山牌がありません！")
            return None
        tile = self.wall.pop()
        player.hand.append(tile)
        player.hand.sort()
        return tile

    def check_win(self, player):
        """
        完全 DFS：4 面子 + 1 雀頭 判定（ソーズ 1‑9 のみ）
        """
        counts = Counter(player.hand)

        # ペア候補をすべて試す
        for t in range(1, 10):
            if counts[t] >= 2:
                cnt = counts.copy()
                cnt[t] -= 2
                if self._dfs_meld(cnt):
                    return True
        return False

    def _dfs_meld(self, cnt):
        """cnt がすべて 0 になれば True"""
        # 残り牌の最小値を探す
        for t in range(1, 10):
            if cnt[t]:
                break
        else:
            return True   # すべて 0 ⇒ 完了

        # 刻子を作る
        if cnt[t] >= 3:
            cnt[t] -= 3
            if self._dfs_meld(cnt):
                return True
            cnt[t] += 3

        # 順子を作る
        if t <= 7 and cnt[t+1] and cnt[t+2]:
            cnt[t]   -= 1
            cnt[t+1] -= 1
            cnt[t+2] -= 1
            if self._dfs_meld(cnt):
                return True
            cnt[t]   += 1
            cnt[t+1] += 1
            cnt[t+2] += 1

        return False

    # ヘルパ: 残り牌がすべて面子に分解できるか
    def _all_meld(self, counts):
        # 残っている最小の牌から順に抜いていく
        for t in range(1, 10):
            while counts[t]:
                # 刻子が作れる
                if counts[t] >= 3:
                    counts[t] -= 3
                    continue
                # 順子が作れるかチェック
                if t + 2 > 9 or counts[t+1] == 0 or counts[t+2] == 0:
                    return False
                counts[t]   -= 1
                counts[t+1] -= 1
                counts[t+2] -= 1
        return True

    def player_draw_and_check_win(self, player):
        tile = self.draw_tile(player)
        if tile is None:
            return None, False
        is_win = self.check_win(player)
        return tile, is_win

    def switch_turn(self):
        idx = self.players.index(self.current_turn)
        self.current_turn = self.players[1 - idx]

    def is_game_over(self):
        return not self.wall

    def get_wall_count(self):
        return len(self.wall)

    def is_my_turn(self, player):
        return self.current_turn == player

    def enumerate_hand(self, player):
        return list(enumerate(player.hand))

    def check_win_after_discard(self, player):
        return self.check_win(player)
    
    def current_turn_name(self):
        return f"Player{self.current_turn}"
    
    def discard_tile(self, player: "Player", tile: int):
        """互換ラッパー：CLI 版 play_tile を転用"""
        # play_tile には (player, tile) で渡す想定
        if hasattr(self, "play_tile"):
            self.play_tile(player, tile)
        else:
            raise AttributeError("play_tile() が実装されていません")    