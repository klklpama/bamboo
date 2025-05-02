import random
from .player import Player

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
        counts = {}
        for tile in player.hand:
            counts[tile] = counts.get(tile, 0) + 1

        sets = sum(count // 3 for count in counts.values())
        pairs = sum(1 for count in counts.values() if count % 3 == 2)

        return sets == 4 and pairs == 1

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
