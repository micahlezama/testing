from typing import Any
from colorama import Style, Fore
import models.game
import network

_DIFFICULTIES = ['Normal', 'Very Hard', 'Super Hard 1', 'Super Hard 2', 'Super Hard 3']


class StageService:
    @staticmethod
    def get_friend(stage_id: int, difficulty: int):
        """Fetch supporter or CPU friend safely for a given stage."""
        if difficulty < 0 or difficulty >= len(_DIFFICULTIES):
            print(f"[StageService] ⚠️ Invalid difficulty index: {difficulty}. Valid range: 0-{len(_DIFFICULTIES)-1}")
            difficulty_name = f"Unknown({difficulty})"
        else:
            difficulty_name = _DIFFICULTIES[difficulty]

        #print(f"[StageService] Fetching supporters for stage {stage_id} ({difficulty_name})...")
        r = network.get_quests_supporters(stage_id=stage_id, difficulty=difficulty, team_num=1)

        if not isinstance(r, dict):
    
            #print("[DEBUG supporters]", r)

            return None
        if "error" in r:
        
            return None

        if "cpu_supporters" in r:
            difficulty_key = _DIFFICULTIES[difficulty].lower().replace(" ", "_")
            if difficulty_key in r["cpu_supporters"]:
                cpu_friends = r["cpu_supporters"][difficulty_key].get("cpu_friends", [])
                if cpu_friends:
                    #print(f"[StageService] ✅ Using CPU supporter (difficulty: {difficulty_name})")
                    return {
                        "is_cpu": True,
                        "id": cpu_friends[0]["id"],
                        "leader": cpu_friends[0]["card_id"],
                    }

        if "supporters" not in r or not r["supporters"]:
            #print(f"[StageService] ⚠️ No supporters found for stage {stage_id} ({difficulty_name})")
            return None

        supporter = r["supporters"][0]


        return {
            "is_cpu": False,
            
            "id": supporter.get("id"),
            "leader": supporter.get("leader"),
        }

    # ✅ Add this new method to start quest safely
    @staticmethod
    def start_stage(stage_id: int, sign: Any):
        """Start quest with proper error handling."""
        #print(f"[StageService] Starting stage {stage_id}...")
        res = network.post_quests_sugoroku_start(stage_id, sign)
        res['result'] = 'failed'

        if isinstance(res, dict):
            if "sign" in res:
                res['result'] = 'success'
                return res
            elif "error" in res:
                err = res["error"]
                err_code = err.get("code") if isinstance(err, dict) else str(err)

                if err_code == "unavailable_quest":
                    print(f"[Stage] ⚠️ Quest {stage_id} is unavailable — skipping.")
                elif err_code == "invalid_token":
                    res['result'] = 'relogin'
                elif err_code == "active_record/record_not_found":
                    print(Fore.RED + "[Stage] Quest not found." + Style.RESET_ALL)
                elif err_code == "invalid_area_conditions_potential_releasable":
                    print(Fore.RED + "[Stage] You do not meet the conditions for this event." + Style.RESET_ALL)
                elif err_code == 'act_is_not_enough':
                    res['result'] = 'low_stamina'
                elif err_code == "the_number_of_cards_must_be_less_than_or_equal_to_the_capacity":
                    res['result'] = 'full_box'
                else:
                    print(f"[Stage] Unhandled error: {err_code}")
        return res

    @staticmethod
    def get_sign(friend, kagi, difficulty: int, selected_team_num: int):
        """Generate the encrypted stage sign payload."""
        if not friend:
            print("[StageService] ❌ No valid friend found. Cannot build sign.")
            return None

        if not friend["is_cpu"]:
            payload = {
                "bgm_filename": "",
                "difficulty": difficulty,
                "friend_id": int(friend["id"]),
                "is_playing_script": True,
                "selected_team_num": selected_team_num,
                "support_leader": friend["leader"],
            }
            if kagi is not None:
                payload["eventkagi_item_id"] = kagi
        else:
            payload = {
                "difficulty": difficulty,
                "cpu_friend_id": int(friend["id"]),
                "is_playing_script": True,
                "selected_team_num": selected_team_num,
            }
            if kagi is not None:
                payload["eventkagi_item_id"] = kagi

        return payload

    @staticmethod
    def get_difficulty_name(difficulty: int) -> str:
        if 0 <= difficulty < len(_DIFFICULTIES):
            return _DIFFICULTIES[difficulty]
        return f"Unknown({difficulty})"

    @staticmethod
    def print_rewards(sign: Any):
        if 'items' in sign:
            supportitems = []
            awakeningitems = []
            trainingitems = []
            potentialitems = []
            treasureitems = []
            carditems = []
            trainingfields = []
            stones = 0
            supportitemsset = set()
            awakeningitemsset = set()
            trainingitemsset = set()
            potentialitemsset = set()
            treasureitemsset = set()
            carditemsset = set()
            trainingfieldsset = set()

            if 'quest_clear_rewards' in sign:
                for x in sign['quest_clear_rewards']:
                    if x['item_type'] == 'Point::Stone':
                        stones += x['amount']

            for x in sign['items']:
                if x['item_type'] == 'SupportItem':

                    # print('' + SupportItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    for i in range(x['quantity']):
                        supportitems.append(x['item_id'])
                    supportitemsset.add(x['item_id'])
                elif x['item_type'] == 'PotentialItem':

                    # print('' + PotentialItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    for i in range(x['quantity']):
                        potentialitems.append(x['item_id'])
                    potentialitemsset.add(x['item_id'])
                elif x['item_type'] == 'TrainingItem':

                    # print('' + TrainingItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    for i in range(x['quantity']):
                        trainingitems.append(x['item_id'])
                    trainingitemsset.add(x['item_id'])
                elif x['item_type'] == 'AwakeningItem':

                    # print('' + AwakeningItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    for i in range(x['quantity']):
                        awakeningitems.append(x['item_id'])
                    awakeningitemsset.add(x['item_id'])
                elif x['item_type'] == 'TreasureItem':

                    # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    for i in range(x['quantity']):
                        treasureitems.append(x['item_id'])
                    treasureitemsset.add(x['item_id'])
                elif x['item_type'] == 'Card':

                    # card = Cards.find(x['item_id'])

                    carditems.append(x['item_id'])
                    carditemsset.add(x['item_id'])
                elif x['item_type'] == 'Point::Stone':

                    #                print('' + card.name + '['+rarity+']'+ ' x '+str(x['quantity']))
                    # print('' + TreasureItems.find(x['item_id']).name + ' x '+str(x['quantity']))

                    stones += 1
                elif x['item_type'] == 'TrainingField':

                    # card = Cards.find(x['item_id'])

                    for i in range(x['quantity']):
                        trainingfields.append(x['item_id'])
                    trainingfieldsset.add(x['item_id'])
                else:
                    print(x['item_type'])

            for x in supportitemsset:
                support_item: models.game.SupportItems = models.game.SupportItems.get_by_id(x)
                print(Fore.CYAN + Style.BRIGHT + support_item.name + ' x' + str(supportitems.count(x)))

            for x in awakeningitemsset:
                awakening_item: models.game.AwakeningItems = models.game.AwakeningItems.get_by_id(x)
                print(Fore.MAGENTA + Style.BRIGHT + awakening_item.name + ' x' + str(     
                    awakeningitems.count(x)))

            for x in trainingitemsset:
                training_item: models.game.TrainingItems = models.game.TrainingItems.get_by_id(x)
                print(Fore.RED + Style.BRIGHT + training_item.name + ' x' + str(trainingitems.count(x)))

            for x in potentialitemsset:
                potential_item: models.game.PotentialItems = models.game.PotentialItems.get_by_id(x)
                print(potential_item.name + ' x' + str(potentialitems.count(x)))

            for x in treasureitemsset:
                treasure_item: models.game.TreasureItems = models.game.TreasureItems.get_by_id(x)
                print(
                    Fore.GREEN + Style.BRIGHT + treasure_item.name + ' x' + str(treasureitems.count(x)))

            for x in trainingfieldsset:
                training_field: models.game.TrainingFields = models.game.TrainingFields.get_by_id(x)
                print(training_field.name + ' x' + str(trainingfields.count(x)))
