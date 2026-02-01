from config import GameContext

NAME = 'exit'
DESCRIPTION = 'Close the bot'
CONTEXT = [GameContext.AUTH, GameContext.GAME]
CATEGORY = 'Account management'

def run():
    print('bye-bye king...')
    return  # <-- DO NOT EXIT THE PROCESS
