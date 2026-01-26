import FreeSimpleGUI as sg
from colorama import Fore, Style

import config
import network

from models import game
from commands import area 
from commands.awaken import awaken_team
from commands.change_team import build_team


NAME = 'link-farm'
DESCRIPTION = 'Farm and increase character link skill level'
CONTEXT = [config.GameContext.GAME]

def run():
    ###Get user cards
    print(Fore.CYAN + Style.BRIGHT + 'Fetching user cards...')
    master_cards = network.get_cards()['cards']

    ###Sort user cards into a list of dictionaries with attributes
    print(Fore.CYAN + Style.BRIGHT + 'Fetching card attributes...')
    card_list = []
    for card in master_cards:
        #link_losl = card['link_skill_lvs']

        ###Get card collection object from database
        db_card = game.Cards.get_by_id(card['card_id'])

        ###Get card link_skills list
        link_skills = []
        link_levels = []

        for li in range(1, 8):
            if eval(f"db_card.link_skill{li}_id"):
                link_skills.append(game.LinkSkills.get_by_id(eval(f"db_card.link_skill{li}_id")))

            for lsk in card['link_skill_lvs']:
                slv = lsk['skill_lv']
                link_levels.append(slv)
                break
            else:
                link_levels.append(0)

        dict = {
            'ID': db_card.id,
            'Name': db_card.name,
            'Hercule': db_card.is_selling_only,
            'HP': db_card.hp_init,
            'Links': link_skills,
            'Link_levels': link_levels,
            'UniqueID': card['id']
        }
        card_list.append(dict)

    print(Fore.GREEN + Style.BRIGHT + "Done...")

    ###Sort cards
    card_list = sorted(card_list, key=lambda k: k['Name'])

    ###Define cards to display
    cards_to_display_dicts = []
    cards_to_display = []
    # Take cards in card_list that aren't hercule statues or kais?
    for char in card_list:
        cards_to_display_dicts.append(char)
        if char['Hercule'] != 1 and char['HP'] > 5:
            for i, ls in enumerate(char['Links']):
                cards_to_display.append(
                    str(char['UniqueID']) + ' | ' + str(char['Name'])
                    + ' | ' + str(ls.id) + ' | ' + str(ls.name) + ' | ' + str(char['Link_levels'][i]))


    ###Define window layout
    col1 = [[sg.Listbox(values=(cards_to_display), size=(60, 20), key='CARDS')],
            [sg.Text('Target level: '),
             sg.Spin([i for i in range(1, 11)], initial_value=10, size=(5, None), key='TARGET_LEVEL'),
             sg.Button(button_text='Choose Card & Skill', key='choose_card'),
             sg.Button(button_text='Choose All', key='choose_all')],
            [sg.Listbox(values=([]), size=(60, 6), key='CARDS_CHOSEN')],
             [sg.Button(button_text='Confirm and run links farm', key='confirm_setup')]]

    layout = [[sg.Column(col1)]]
    window = sg.Window('Link Skills Farm', grab_anywhere=True, keep_on_top=True).Layout(layout)

    ###Begin window loop
    chosen_links = []

    ###
    chosen_skill_unique_ids = []
    skills_levelup = []
    chosen_skill_mix = []
    chosen_cards_to_display = []

    while True:
        event, values = window.Read()

        if event is None:
            return 0

        if event == 'choose_card':
            if len(values['CARDS']) < 1:
                continue
            # Get ID of chosen card to send to bandai
            chosen_line = values['CARDS'][0]
            char_unique_id, _,  skill_id, skill_name, _ = chosen_line.split(' | ')
            chosen_skill_unique_ids.append(int(char_unique_id))
            skills_levelup.append((int(char_unique_id), int(skill_id), int(values['TARGET_LEVEL'])))
            chosen_skill_mix.append(skill_name + str(char_unique_id))

            # Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_all':
            # Get ID of chosen card to send to bandai
            for chosen_line in window['CARDS'].get_list_values():
                char_unique_id, _,  skill_id, skill_name, _ = chosen_line.split(' | ')
                chosen_skill_unique_ids.append(int(char_unique_id))
                skills_levelup.append((int(char_unique_id), int(skill_id), int(values['TARGET_LEVEL'])))
                chosen_skill_mix.append(skill_name + str(char_unique_id))

                # Chosen cards to display in lower box
                chosen_cards_to_display.append(chosen_line)

        if event == 'confirm_setup':
            break

        ###Re-populate cards to display, checking filter criteria
        cards_to_display[:] = []
        for char in cards_to_display_dicts:
            for i, ls in enumerate(char['Links']):
                if (ls.name + str(char['UniqueID'])) in chosen_skill_mix:
                    continue
                cards_to_display.append(
                    str(char['UniqueID']) + ' | ' + str(char['Name'])
                    + ' | ' + str(ls.id) + ' | ' + str(ls.name) + ' | ' + str(char['Link_levels'][i]))

        window.find_element('CARDS').Update(values=cards_to_display)
        window.find_element('CARDS_CHOSEN').Update(values=chosen_cards_to_display)

    window.Close()

    ltm = []
    while skills_levelup:
        link_fulfilled(skills_levelup)
        tuids, tids = team_aids(skills_levelup, master_cards)
        if set(tuids) != set(ltm):
            tuids = awaken_team(tuids, tids, master_cards)
            ltm = tuids.copy()
            master_cards = network.get_cards()['cards']
            build_team(tuids, 1, master_cards)
        link_farm()

    print(Fore.GREEN + Style.BRIGHT + "Link level up complete!")

    return 0

def team_aids(locsl, lomc):
    louci = []
    loci = []
    for tcid, _, _ in locsl:
        for mc in lomc:
            if mc['id'] == tcid: 
                loci.append(mc['card_id'])
                break
        louci.append(mc['id'])
    return louci, loci

cuai = 5

def link_farm():
    global cuai
    area.run(cuai, skip=False)
    cuai = cuai + 1 if cuai < 36 else 5

def link_fulfilled(locsl):
    ucards = network.get_cards()['cards']
    rr = True

    for i, (tcid, tsid, tlv) in enumerate(locsl.copy()):
        for ucard in ucards:
            if ucard['id'] == tcid:
                louls = ucard['link_skill_lvs']
                for uskl in louls:
                    sid, slv = uskl['id'], uskl['skill_lv']
                    if sid == tsid:
                        if slv < tlv:
                            rr = False
                        else:
                            locsl.pop(i)
                        break
                else:
                    rr = False
        
    return rr 
