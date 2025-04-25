# bamboo_core/game.py

import random

class Game:
    def __init__(self):
        self.deck = [i for i in range(1, 10)] * 4
        random.shuffle(self.deck)
        self.hands = {
            "Player1": [self.deck.pop() for _ in range(3)],
            "Player2": [self.deck.pop() for _ in range(3)],
        }
        self.turn = "Player1"

    def get_hand(self, player):
        return self.hands[player]

    def play_card(self, player, index):
        if player != self.turn:
            raise ValueError("Not your turn!")
        if index < 0 or index >= len(self.hands[player]):
            raise IndexError("Invalid card index")
        played_card = self.hands[player].pop(index)
        print(f"{player} played {played_card}")
        self.turn = "Player2" if self.turn == "Player1" else "Player1"

    def draw_card(self):
        if self.deck:
            self.hands[self.turn].append(self.deck.pop())
        else:
            print("The deck is empty!")

    def is_game_over(self):
        return not self.deck
