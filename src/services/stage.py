from typing import Any

from colorama import Style, Fore

import models.game
import network

_DIFFICULTIES = ['normal', 'very_hard', 'super_hard1', 'super_hard2', 'super_hard3']


class StageService:
    @staticmethod
    def get_friend(stage_id: int, difficulty: int):
        # Returns supporter for given stage_id & difficulty
        # Chooses cpu_supporter if possible
        r = network.get_quests_supporters(
            stage_id=stage_id,
            difficulty=difficulty,
            team_num=1
        )

        # If CPU supporter available, choose it every time
        difficulty_name = _DIFFICULTIES[difficulty]
        if 'cpu_supporters' in r and difficulty_name in r['cpu_supporters']:
            cpu_friends = r['cpu_supporters'][difficulty_name]['cpu_friends']
            if len(cpu_friends) > 0:
                return {
                    'is_cpu': True,
                    'id': cpu_friends[0]['id'],
                    'leader': cpu_friends[0]['card_id']
                }
        
        return {
            'is_cpu': False,
            'id': r['supporters'][0]['id'],
            'leader': r['supporters'][0]['leader']
        }

    @staticmethod
    def get_sign(
        friend,
        kagi,
        difficulty: int,
        selected_team_num: int
    ):
    #{'bgm_filename': '', 'difficulty': 0, 'friend_id': 1239177007, 
    # 'is_playing_script': True, 'selected_team_num': 1, 
    # 'support_leader': {'awakening_route_id': 7439, 
    # 'card_decoration_id': 0, 'card_id': 1025801, 
    # 'equipment_skill_items': [{'equipment_skill_item_id': 0, 'grade': 'bronze', 'slot': 0}, 
    # {'equipment_skill_item_id': 0, 'grade': 'silver', 'slot': 0}, {'equipment_skill_item_id': 0, 'grade': 'gold', 'slot': 0}], 'exchangeable_item_id': None, 'exp': 15000000, 'id': 1756178246, 'is_favorite': True, 'is_released_potential': True, 'link_skill_lvs': [{'id': 37, 'skill_lv': 5}, {'id': 42, 'skill_lv': 5}, {'id': 47, 'skill_lv': 7}, {'id': 36, 'skill_lv': 6}, {'id': 45, 'skill_lv': 5}, {'id': 60, 'skill_lv': 6}, {'id': 109, 'skill_lv': 6}], 'optimal_awakening_step': 7, 'potential_parameters': [{'parameter_type': 'Hp', 'total_value': 4000}, {'parameter_type': 'Atk'arameter_id': 1, 'parameter_type': 'Skill', 'total_value': 0}, {'parameter_id': 2, 'parameter_type': 'Skill', 'total_value': 9}, {'parameter_id': 3, 'parameter_type': 'Skill', 'total_value': 17}, {'parameter_id': 4, 'parameter_type': 'Skill', 'total_value': 8}, {'parameter_id': 5, 'parameter_type': 'Skill', 'total_value': 7}, {'parameter_id': 6, 'parameter_type': 'Skill', 'total_value': 8}, {'parameter_id': 7, 'parameter_type': 'Skill', 'total_value': 8}], 'released_rate': 79.3413, 'skill_lv': 15, 'unlocked_square_statuses': [0, 2, 2, 0]}, 
    # 'support_user_card_id': 1756178246}
        if not friend['is_cpu']:
            if kagi is not None:
                return {'bgm_filename':'', 'difficulty': difficulty, 'eventkagi_item_id': kagi, 'friend_id': int(friend['id']),
                        'is_playing_script': True, 'selected_team_num': selected_team_num,
                        'support_leader': friend['leader']}
                                          
                                          
            else:
                return {'bgm_filename':'', 'difficulty': difficulty, 'friend_id': int(friend['id']), 'is_playing_script': True,
                        'selected_team_num': selected_team_num,
                        'support_leader': friend['leader']}

        if kagi != None:
            return {'difficulty': difficulty, 'eventkagi_item_id': kagi, 'cpu_friend_id': int(friend['id']),
                    'is_playing_script': True, 'selected_team_num': selected_team_num}

        return {'difficulty': difficulty, 'cpu_friend_id': int(friend['id']), 'is_playing_script': True,
                'selected_team_num': selected_team_num}

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

            for x in carditemsset:
                card: models.game.Cards = models.game.Cards.get_by_id(x)
                print(card.name + ' x' + str(carditems.count(x)))

            print(Fore.YELLOW + Style.BRIGHT + 'Stones x' + str(stones))

        zeni = '{:,}'.format(sign['zeni'])
        print('Zeni: ' + zeni)
        if 'gasha_point' in sign:
            print('Friend Points: ' + str(sign['gasha_point']))
