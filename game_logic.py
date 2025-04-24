import random

SUITS = list(range(1, 10)) * 4  # 1〜9のソーズ×4

def draw_hand(deck, n=3):
    return [deck.pop() for _ in range(n)]

def remove_card(hand, chosen_index):
    return hand[:chosen_index] + hand[chosen_index+1:]

def format_hand(hand):
    return ' '.join(map(str, hand))

def init_deck():
    deck = SUITS.copy()
    random.shuffle(deck)
    return deck