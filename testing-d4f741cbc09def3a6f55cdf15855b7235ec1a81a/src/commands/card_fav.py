import config
import network

NAME = 'card fav'
DESCRIPTION = 'Favorite a unit of each card'
CONTEXT = [config.GameContext.GAME]
CATEGORY = 'Box management'

def run():
    print('test')
    cards = network.get_cards()
    print(cards)
