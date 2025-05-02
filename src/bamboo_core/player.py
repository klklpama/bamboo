class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw(self, card):
        self.hand.append(card)

    def discard(self, index):
        return self.hand.pop(index)

    def show_hand(self):
        return self.hand