import random

def create_wall():
    """
    山牌（ウォール）を生成・シャッフルする
    """
    # ソーズのみを使用するので、各数字4枚ずつ
    wall = [f"{num}s" for num in range(1, 10) for _ in range(4)]
    random.shuffle(wall)
    return wall