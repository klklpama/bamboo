import random

def init_hand():
    return random.sample(range(1, 10), 3)

def display_hand(player, hand):
    print(f"\n🎴 {player} のターン")
    print(f"あなたの手札: {hand}")

def choose_card(hand):
    while True:
        try:
            idx = int(input("出すカードを選んでください（index: 0〜2）: "))
            if 0 <= idx < len(hand):
                return hand.pop(idx)
            else:
                print("⚠️ 無効な番号です。")
        except Exception:
            print("⚠️ 数字で入力してください。")

def main():
    player1_hand = init_hand()
    player2_hand = init_hand()

    turn = 0
    last_play = {"Player 1": None, "Player 2": None}

    while player1_hand and player2_hand:
        current_player = "Player 1" if turn % 2 == 0 else "Player 2"
        hand = player1_hand if current_player == "Player 1" else player2_hand

        display_hand(current_player, hand)
        if last_play[current_player] is not None:
            print(f"🟩 相手の前回の手: {last_play[current_player]}")

        played = choose_card(hand)
        last_play[current_player] = played
        print(f"{'🟥' if current_player == 'Player 1' else '🟦'} あなたは {played} を出しました！")

        turn += 1

    print("\n🟠 ゲーム終了！")

if __name__ == "__main__":
    main()
