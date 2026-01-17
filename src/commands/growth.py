import FreeSimpleGUI as sg
from colorama import Fore, Style

import config
import network

from models import game


NAME = 'farm link'
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
        link_losl = card['link_skill_lvs']

        ###Get card collection object from database
        db_card = game.Cards.get_by_id(card['card_id'])

        ###Get card link_skills list
        link_skills = []
        for li in range(1, 8):
            if eval(f"db_card.link_skill{li}_id"):
                link_skills.append(game.LinkSkills.get_by_id(eval(f"db_card.link_skill{li}_id")))

        dict = {
            'ID': db_card.id,
            'Name': db_card.name,
            'Hercule': db_card.is_selling_only,
            'HP': db_card.hp_init,
            'Links': link_skills,
            'Link_levels': link_losl,
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
            for ls in char['Links']:
                cards_to_display.append(
                    str(char['UniqueID']) + ' | ' + str(char['Name'])
                    + ' | ' + str(ls.id) + ' | ' + str(ls.name))


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
            char_unique_id, _,  skill_id, skill_name = chosen_line.split(' | ')
            chosen_skill_unique_ids.append(int(char_unique_id))
            skills_levelup.append((char_unique_id, skill_id, values['TARGET_LEVEL']))
            chosen_skill_mix.append(skill_name + str(char_unique_id))

            # Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_all':
            # Get ID of chosen card to send to bandai
            for chosen_line in window['CARDS'].get_list_values():
                char_unique_id, _,  skill_id, skill_name = chosen_line.split(' | ')
                chosen_skill_unique_ids.append(int(char_unique_id))
                skills_levelup.append((char_unique_id, skill_id, values['TARGET_LEVEL']))
                chosen_skill_mix.append(skill_name + str(char_unique_id))

                # Chosen cards to display in lower box
                chosen_cards_to_display.append(chosen_line)

        if event == 'confirm_setup':
            break

        ###Re-populate cards to display, checking filter criteria
        cards_to_display[:] = []
        for char in cards_to_display_dicts:
            for ls in char['Links']:
                if (ls.name + str(char['UniqueID'])) in chosen_skill_mix:
                    continue
                cards_to_display.append(
                    str(char['UniqueID']) + ' | ' + str(char['Name'])
                    + ' | ' + str(ls.id) + ' | ' + str(ls.name))

        window.find_element('CARDS').Update(values=cards_to_display)
        window.find_element('CARDS_CHOSEN').Update(values=chosen_cards_to_display)

    window.Close()
    ##Send Link level up
    r = network.post_link_lvl_up()
    if 'error' in r:
        print(Fore.RED + Style.BRIGHT + str(r))
    else:
        print(Fore.GREEN + Style.BRIGHT + "Link level up complete!")

    return 0
