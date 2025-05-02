import random

def create_wall():
    """
    山牌（ウォール）を生成・シャッフルする
    """
    # ソーズのみを使用するので、各数字4枚ずつ
    wall = [f"{num}s" for num in range(1, 10) for _ in range(4)]
    random.shuffle(wall)
    return wall

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 50000  # 初期スコア

    def receive_tiles(self, tiles):
        """
        プレイヤーに牌を配る
        """
        self.hand.extend(tiles)
        self.hand.sort()  # 牌を昇順にソートしておくと便利
