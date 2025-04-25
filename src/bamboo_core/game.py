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

        # 各プレイヤーに13枚ずつ配る
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
        超シンプルな上がり判定（3枚セット4つ＋2枚ペア）
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
        牌を引き、その後勝利判定を行う。
        """
        tile = self.draw_tile(player_id)
        if tile is None:
            return None, False
        is_win = self.check_win(player_id)
        return tile, is_win

    def switch_turn(self):
        self.current_turn = 2 if self.current_turn == 1 else 1

    def end_turn(self, player_id):
        if self.current_turn != player_id:
            raise ValueError("あなたのターンではありません。")
        self.switch_turn()

    def handle_message(self, player_id, message):
        try:
            tile = int(str(message).strip())
            self.discard_tile(player_id, tile)
            return f"プレイヤー{player_id}が「{tile}」を捨てました\n🀄 手札：{hand}"
        except ValueError:
            return f"❌ 無効な入力です：{message}"

    def get_hand(self, player_id):
        return self.players[player_id].hand

    def get_deck_count(self):
        return len(self.deck)

    def is_my_turn(self, player_id):
        return self.current_turn == player_id
