from config import GameContext
from services.command import CommandService

NAME = 'reload commands'
DESCRIPTION = 'reload commands from the commands directory'
CONTEXT = [GameContext.AUTH, GameContext.GAME]
CATEGORY = 'Speciality Commands'
run = CommandService.load
