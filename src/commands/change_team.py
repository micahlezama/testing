import FreeSimpleGUI as sg
from colorama import Fore, Style

import network
from models import game
from utils.dbutils import card_chid

from config import GameContext

NAME = 'change-team'
DESCRIPTION = 'Change your deck'
CONTEXT = [GameContext.GAME]
CATEGORY = 'Box management'

def fill_team(locui, ucards, lochid):
    for ucard in ucards:
        chid = card_chid(ucard['card_id'])
        if chid in lochid:
            continue
        for cui in locui:
            if ucard['id'] == cui:
                break
        else:
            locui.append(ucard['id'])
            lochid.append(chid)
            if len(locui) == 6:
                break
    return locui

def remove_same_char(locui, ucards):
    lochid = []
    nlocui = []
    for cui in locui:
        for ucard in ucards:
            if ucard['id'] == cui:
                chid = card_chid(ucard['card_id'])
                if not (chid in lochid):
                    lochid.append(chid)
                    nlocui.append(cui)
    return nlocui, lochid

def build_team(locui, deckn, ucards):
    locui, lochid = remove_same_char(locui, ucards)
    if len(locui) < 6:
        print(Fore.YELLOW + f'{len(locui)} Awakened characters, filling the rest...')
        locui = fill_team(locui, ucards, lochid)
    elif len(locui) > 6:
        locui = locui[:6]

    r = network.post_teams(
        selected_team_num=1,
        user_card_teams=[
            {'num': deckn, 'user_card_ids': locui}
        ]
    )

    if 'error' in r:
        print(Fore.RED + Style.BRIGHT + str(r))
    else:
        print(Fore.GREEN + Style.BRIGHT + "Deck updated!")

def run():
    # Needs to have translation properly implemented!

    ###Get user deck to change
    chosen_deck = int(input("Enter the deck number you would like to change: "))

    ###Get user cards
    print(Fore.CYAN + Style.BRIGHT + 'Fetching user cards...')
    master_cards = network.get_cards()['cards']
    print(Fore.GREEN + Style.BRIGHT + 'Done...')

    ###Sort user cards into a list of dictionaries with attributes
    print(Fore.CYAN + Style.BRIGHT + 'Fetching card attributes...')
    card_list = []
    for card in master_cards:
        ###Get card collection object from database
        db_card = game.Cards.get_by_id(card['card_id'])
        # db_card = config.Cards.where('id','=',card['card_id']).first()

        ###Get card rarity
        if db_card.rarity == 0:
            rarity = 'N'
        elif db_card.rarity == 1:
            rarity = 'R'
        elif db_card.rarity == 2:
            rarity = 'SR'
        elif db_card.rarity == 3:
            rarity = 'SSR'
        elif db_card.rarity == 4:
            rarity = 'UR'
        elif db_card.rarity == 5:
            rarity = 'LR'
        ###Get card Type
        if str(db_card.element)[-1] == '0':
            type = '[AGL] '
        elif str(db_card.element)[-1] == '1':
            type = '[TEQ] '
        elif str(db_card.element)[-1] == '2':
            type = '[INT] '
        elif str(db_card.element)[-1] == '3':
            type = '[STR] '
        elif str(db_card.element)[-1] == '4':
            type = '[PHY] '
        ###Get card categories list
        categories = []
        # Get category id's given card id
        card_card_categories = game.CardCardCategories.select().where(game.CardCardCategories.card_id == db_card.id)

        for category in card_card_categories:
            categories.append(game.CardCategories.get_by_id(category.card_category_id).name)
        ###Get card link_skills list
        link_skills = []
        for li in range(1, 8):
            if eval(f"db_card.link_skill{li}_id"):
                link_skills.append(game.LinkSkills.get_by_id(eval(f"db_card.link_skill{li}_id")).name)

        dict = {
            'ID': db_card.id,
            'Rarity': rarity,
            'Name': db_card.name,
            'Type': type,
            'Cost': db_card.cost,
            'Hercule': db_card.is_selling_only,
            'HP': db_card.hp_init,
            'Categories': categories,
            'Links': link_skills,
            'UniqueID': card['id']
        }
        card_list.append(dict)
    print(Fore.GREEN + Style.BRIGHT + "Done...")

    ###Sort cards
    print(Fore.CYAN + Style.BRIGHT + "Sorting cards...")
    card_list = sorted(card_list, key=lambda k: k['Name'])
    card_list = sorted(card_list, key=lambda k: k['Rarity'])
    card_list = sorted(card_list, key=lambda k: k['Cost'])
    print(Fore.GREEN + Style.BRIGHT + "Done...")
    ###Define cards to display
    cards_to_display_dicts = []
    cards_to_display = []
    # Take cards in card_list that aren't hercule statues or kais?
    for char in card_list:
        if char['Hercule'] != 1 and char['HP'] > 5:
            cards_to_display_dicts.append(char)
            cards_to_display.append(
                char['Type'] + char['Rarity'] + ' ' + char['Name'] + ' | ' + str(char['ID']) + ' | ' + str(
                    char['UniqueID']))

    ###Define links to display
    links_master = []
    for link in game.LinkSkills.select():
        links_master.append(link.name)

    links_to_display = sorted(links_master)

    ###Define categories to display
    categories_master = []
    for category in game.CardCategories.select():
        categories_master.append(game.CardCategories.get_by_id(category.id).name)

    categories_to_display = sorted(categories_master)

    rarities_to_display = ['N',
                           'R',
                           'SR',
                           'SSR',
                           'UR',
                           'LR']

    ###Define window layout

    col1 = [[sg.Listbox(values=(cards_to_display), size=(60, 20), key='CARDS')],
            [sg.Listbox(values=([]), size=(60, 6), key='CARDS_CHOSEN')],
            [sg.Button(button_text='Choose Card', key='choose_card'),
             sg.Button(button_text='Confirm Team', key='confirm_team')]]

    col2 = [[sg.Listbox(values=(sorted(categories_to_display)), size=(25, 20), key='CATEGORIES')],
            [sg.Listbox(values=([]), size=(25, 6), key='CATEGORIES_CHOSEN')],
            [sg.Button(button_text='Choose Categories', key='choose_categories'),
             sg.Button(button_text='Clear Categories', key='clear_categories')]]

    col3 = [[sg.Listbox(values=(sorted(links_to_display)), size=(25, 20), key='LINKS')],
            [sg.Listbox(values=([]), size=(25, 6), key='LINKS_CHOSEN')],
            [sg.Button(button_text='Choose Links', key='choose_links'),
             sg.Button(button_text='Clear Links', key='clear_links')]]

    col4 = [[sg.Listbox(values=rarities_to_display, size=(20, 20), key='RARITY')],
            [sg.Listbox(values=([]), size=(20, 6), key='RARITY_CHOSEN')],
            [sg.Button(button_text='Choose Rarity', key='choose_rarity'),
             sg.Button(button_text='Clear Rarities', key='clear_rarity')]]

    layout = [[sg.Column(col1), sg.Column(col2), sg.Column(col3), sg.Column(col4)]]
    window = sg.Window('Deck Update', grab_anywhere=True, keep_on_top=True).Layout(layout)

    ###Begin window loop
    chosen_links = []
    chosen_categories = []
    chosen_rarities = []

    ###
    chosen_cards_ids = []
    chosen_cards_unique_ids = []
    chosen_cards_names = []
    chosen_cards_to_display = []

    while len(chosen_cards_ids) < 6:
        event, values = window.Read()

        if event is None:
            return 0

        if event == 'choose_card':
            if len(values['CARDS']) < 1:
                continue
            # Get ID of chosen card to send to bandai
            chosen_line = values['CARDS'][0]
            char_name, char_id, char_unique_id = chosen_line.split(' | ')
            chosen_cards_ids.append(int(char_id))
            chosen_cards_unique_ids.append(int(char_unique_id))
            chosen_cards_names.append(game.Cards.get_by_id(char_id).name)

            # Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_categories':
            for category in values['CATEGORIES']:
                chosen_categories.append(category)
                categories_to_display.remove(category)

        if event == 'clear_categories':
            categories_to_display.extend(chosen_categories)
            chosen_categories[:] = []
            categories_to_display = sorted(categories_to_display)

        if event == 'choose_rarity':
            for rarity in values['RARITY']:
                chosen_rarities.append(rarity)
                rarities_to_display.remove(rarity)

        if event == 'clear_rarity':
            rarities_to_display.extend(chosen_rarities)
            chosen_rarities[:] = []

        if event == 'choose_links':
            for link in values['LINKS']:
                chosen_links.append(link)
                links_to_display.remove(link)

        if event == 'clear_links':
            links_to_display.extend(chosen_links)
            chosen_links[:] = []
            links_to_display = sorted(links_to_display)

        if event == 'confirm_team':
            if len(chosen_cards_unique_ids) < 6:
                if len(chosen_cards_unique_ids) == 0:
                    print(Fore.RED + Style.BRIGHT + 'No cards selected.')
                    return 0
                loop = 6 - len(chosen_cards_unique_ids)
                for i in range(int(loop)):
                    chosen_cards_unique_ids.append('0')
                break

        ###Re-populate cards to display, checking filter criteria
        cards_to_display[:] = []
        for char in cards_to_display_dicts:
            if char['Name'] in chosen_cards_names:
                continue

            if len(chosen_rarities) > 0:
                if not char['Rarity'] in chosen_rarities:
                    continue

            if len(list(set(chosen_links) & set(char['Links']))) != len(chosen_links):
                # print("List intersection")
                continue

            if len(list(set(chosen_categories) & set(char['Categories']))) != len(chosen_categories):
                # print("Category intersectino")
                continue

            cards_to_display.append(
                char['Type'] + char['Rarity'] + ' ' + char['Name'] + ' | ' + str(char['ID']) + ' | ' + str(
                    char['UniqueID']))

        ###Update window elements
        window.find_element('CARDS').Update(values=cards_to_display)
        window.find_element('CARDS_CHOSEN').Update(values=chosen_cards_to_display)
        window.find_element('CATEGORIES').Update(values=categories_to_display)
        window.find_element('CATEGORIES_CHOSEN').Update(values=chosen_categories)
        window.find_element('LINKS').Update(values=links_to_display)
        window.find_element('LINKS_CHOSEN').Update(values=chosen_links)
        window.find_element('RARITY').Update(values=rarities_to_display)
        window.find_element('RARITY_CHOSEN').Update(values=chosen_rarities)

    window.Close()
    ###Send selected team to bandai
    build_team(chosen_cards_ids, chosen_deck, master_cards)

    return 0
