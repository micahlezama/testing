import network
from commands.stage import run as run_stage 


import config
NAME = "sell_medals"
DESCRIPTION = "Sells medals."
CONTEXT = [config.GameContext.GAME]
CATEGORY = 'Farming'


def run(*args, **kwargs): print("sell_medals not implemented yet")


# noinspection SyntaxError
def complete_unfinished_events_command():
    events = network.get_events()
    event_ids = []
    for event in events['events']:
        event_ids.append(event['id'])
    event_ids = sorted(event_ids)
    try:
        event_ids.remove(135)
    except:
        None

    ### Complete areas if they are in the current ID pool
    r = network.get_user_areas()
    areas = r['user_areas']
    i = 1
    for area in areas:
        if area['area_id'] in event_ids:
            for stage in area['user_sugoroku_maps']:
                if stage['cleared_count'] == 0:
                    run_stage(str(stage['sugoroku_map_id'])[:-1], str(stage['sugoroku_map_id'])[-1])
                    i += 1
        if i % 30 == 0:
            pass
            #refresh_client_command()
