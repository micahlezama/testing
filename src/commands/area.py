import config
import models.game
from colorama import Fore, Back, Style
from commands import stage
import network
import time

NAME = 'area'
DESCRIPTION = 'Completes all quests within a given area'
CONTEXT = [config.GameContext.GAME]

def run(area_id: int = None):
    if area_id is None:
        print(Fore.RED + "[ERROR] You must specify an area ID (e.g. area 1)" + Fore.RESET)
        return

    print(Fore.YELLOW + f"[DEBUG] Starting area {area_id}..." + Fore.RESET)

    # === 1. Fetch cleared quests ===
    cleared_data = network.get_quests()
    cleared_ids = set()
    for q in cleared_data.get("quests", []):
        if q.get("is_cleared"):
            cleared_ids.add(int(q["id"]))
    print(Fore.CYAN + f"[DEBUG] Found {len(cleared_ids)} cleared stages from API." + Fore.RESET)

    # === 2. Fetch all quests in the selected area ===
    area_quests = list(models.game.Quests.select().where(models.game.Quests.area_id == int(area_id)))
    print(Fore.CYAN + f"[DEBUG] Found {len(area_quests)} quests in area {area_id}." + Fore.RESET)

    total_maps = 0
    quest_maps = []

    # Collect all maps for the area
    for quest in area_quests:
        sugorokus = list(models.game.SugorokuMaps.select().where(models.game.SugorokuMaps.quest_id == quest.id))
        for s in sugorokus:
            total_maps += 1
            quest_maps.append((quest, s))

    print(Fore.CYAN + f"[DEBUG] Total maps to complete: {total_maps}" + Fore.RESET)

    # === 3. Iterate through maps and skip cleared ones ===
    completed = 0
    for i, (quest, s) in enumerate(quest_maps, start=1):
        quest_id = int(s.quest_id)
        stage_id = int(s.id)

        # Skip if already cleared
        if stage_id in cleared_ids:
            print(Fore.YELLOW + f"[SKIP] Stage {stage_id} already cleared. ({quest.name})" + Fore.RESET)
           # user_response = print(Fore.YELLOW + "Would you like to clear it again? Y/N")
            #if user_response() == 'Y':
               # stage_id
            continue
        

        # Execute stage
        print(Back.BLUE + Fore.WHITE + f"Completion of map: {i}/{total_maps} ({round((i / total_maps) * 100)}%)" + Style.RESET_ALL)
        #print(Fore.CYAN + f"Begin stage: {quest.name} {stage_id} | Difficulty: {s.difficulty} Deck: 1" + Fore.RESET)
        try:
            stage.run(quest_id, s.difficulty)
        except Exception as e:
            print(Fore.RED + f"[ERROR] Stage {stage_id} failed: {e}" + Fore.RESET)
            continue
