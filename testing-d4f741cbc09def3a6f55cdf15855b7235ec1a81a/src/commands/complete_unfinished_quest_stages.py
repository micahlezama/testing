import network
from commands.stage import run as run_stage


import config
NAME = "sell_medals"
DESCRIPTION = "Sells medals."
CONTEXT = [config.GameContext.GAME]
CATEGORY = 'Farming'


def run(*args, **kwargs): print("sell_medals not implemented yet")


# noinspection SyntaxError
def complete_unfinished_quest_stages_command():
    # ## Will eventually use this to streamline stuff
    # type: (object, object) -> object

    r = network.get_user_areas()

    maps = []
    for user in r:
        for map in user['user_sugoroku_maps']:
            if map['cleared_count'] == 0 and map['sugoroku_map_id'] < 999999 and map['sugoroku_map_id'] > 100:
                maps.append(map)

    if len(maps) == 0:
        print("No quests to complete!")
        print('--------------------------------------------')
        return 0

    i = 0
    while i == 0:
        # print(maps)
        for map in maps:
            run_stage(str(map['sugoroku_map_id'])[:-1], str(map['sugoroku_map_id'])[-1])

        maps_check = []
        for user in r['user_areas']:
            for map in user['user_sugoroku_maps']:
                if map['cleared_count'] == 0 and map['sugoroku_map_id'] < 999999 and map['sugoroku_map_id'] > 100:
                    maps_check.append(map)
        if maps_check == maps:
            i = 1
        else:
            maps = maps_check
    return 1
