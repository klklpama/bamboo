import random
from .player import Player

class Game:
    def __init__(self):
        self.deck = [i for i in range(1, 10)] * 4  # 1〜9ソーズ4枚ずつ
        random.shuffle(self.deck)

        self.players = {
            1: Player(1),
            2: Player(2),
        }

        self.current_turn = 1  # プレイヤー1からスタート

        # 最初に13枚配る
        for _ in range(13):
            for pid in [1, 2]:
                self.players[pid].hand.append(self.deck.pop())

    def draw_tile(self, player_id):
        if not self.deck:
            return None  # 山札切れ
        tile = self.deck.pop()
        self.players[player_id].hand.append(tile)
        return tile

    def discard_tile(self, player_id, tile):
        if tile not in self.players[player_id].hand:
            raise ValueError(f"プレイヤー{player_id}はその牌を持っていません。")
        self.players[player_id].hand.remove(tile)

    def check_win(self, player_id):
        """
        超シンプル上がり判定（同一牌3枚を4セット＋雀頭1ペア）
        """
        counts = {}
        for tile in self.players[player_id].hand:
            counts[tile] = counts.get(tile, 0) + 1

        sets = 0
        pair = 0
        for count in counts.values():
            sets += count // 3
            if count % 3 == 2:
                pair += 1

        return sets == 4 and pair == 1

    def player_draw_and_check_win(self, player_id):
        """
        牌を引いて、そのまま勝利チェックも行う。
        勝ったらTrueを返す。
        """
        tile = self.draw_tile(player_id)
        if tile is None:
            return None, False  # 山札が切れてる
        is_win = self.check_win(player_id)
        return tile, is_win

    def switch_turn(self):
        self.current_turn = 2 if self.current_turn == 1 else 1

    def get_hand(self, player_id):
        return self.players[player_id].hand

    def get_deck_count(self):
        return len(self.deck)
