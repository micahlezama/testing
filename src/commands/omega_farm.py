import config

import models.game
from colorama import Fore, Back, Style
from commands import stage

NAME = 'omega farm'
DESCRIPTION = 'Completes all quests'
CONTEXT = [config.GameContext.GAME]


def run():
    quests: list[models.game.Quests] = models.game.Quests.select().where(models.game.Quests.area_id > 1)
    total = len(quests) 

    i = 1
    for quest in quests:
        sugorokus: list[models.game.SugorokuMaps] = models.game.SugorokuMaps.select().where(models.game.SugorokuMaps.quest_id == quest.id)
        for sugoroku in sugorokus:
            stage.run(quest.id, sugoroku.difficulty)
        print(Fore.WHITE + Back.BLUE + Style.BRIGHT +
              'Completion of quest: ' + str(i) + '/' + str(total) 
              + ' (' + str(round((i / total) * 100)) + '%)')
        i += 1