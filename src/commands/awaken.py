import FreeSimpleGUI as sg
from colorama import Fore, Style, Back

import config
import network

from models import game
from utils.dbutils import card_exptolv, card_awakened, card_name
from commands.train import train_team, card_curexp


NAME = 'awaken'
DESCRIPTION = 'Select characters to awaken'
CONTEXT = [config.GameContext.GAME]

def awaken_team(locui:list[int], loci: list[int], ucards):
    """
    Try to awaken all cards given
    
    :param louci: list of cards unique ids(network)
    :param loci:  list of cards ids(database)
    """
    car = game.CardAwakeningRoutes
    cas = game.CardAwakenings
    tuids = []
    tmtrnd = False

    for i, cid in enumerate(loci):
        if card_awakened(cid):
            print(Fore.GREEN + f'Card {locui[i]} | {card_name(cid)} already awakened!')
            tuids.append(locui[i])
            continue

        try:
            cuid = locui[i]
            ccar = car.select().where(car.card_id == cid)[0]
            casid = ccar.card_awakening_set_id
            loccas = cas.select().where(cas.card_awakening_set_id == casid)
            awknums = []
            for ca in loccas:
                awknums.append(int(ca.num))
            awkrtid = ccar.id
            if card_curexp(ucards, cuid) >= card_exptolv(cid, -1):
                print(Fore.YELLOW + f'Card {locui[i]} | {card_name(cid)} is trained, starting awakening!')
                ar = network.put_awaken(cuid, awknums, awkrtid) 
            elif not tmtrnd:
                if train_team(locui, loci, ucards, skip_awakened=True) > 0:
                    tmtrnd = True
                ucards = network.get_cards()['cards']
                ar = network.put_awaken(cuid, awknums, awkrtid) 
            else:
                ar = False
            if ar:
                if 'error' in ar:
                    raise Exception(str(ar))
                else:
                    print(Fore.GREEN + f'Card {locui[i]} | {card_name(cid)} awakened!')
                    tuids.append(ar['card']['id'])
        except Exception as e:
            print(Fore.RED + f'Error happened while awakening {cuid}: {e}')
        
    return tuids 

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

        dict = {
            'ID': db_card.id,
            'Name': db_card.name,
            'Hercule': db_card.is_selling_only,
            'HP': db_card.hp_init,
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
            cards_to_display.append(
                str(char['UniqueID']) + ' | ' + str(char['ID']) + 
                ' | ' + str(char['Name']))


    ###Define window layout
    col1 = [[sg.Listbox(values=(cards_to_display), size=(60, 20), key='CARDS')],
            [sg.Button(button_text='Choose Card', key='choose_card'),
             sg.Button(button_text='Choose All', key='choose_all')],
            [sg.Listbox(values=([]), size=(60, 6), key='CARDS_CHOSEN')],
             [sg.Button(button_text='Confirm and awaken', key='confirm_setup')]]

    layout = [[sg.Column(col1)]]
    window = sg.Window('Awaken characters', grab_anywhere=True, keep_on_top=True).Layout(layout)

    ###Begin window loop
    chosen_unique_ids = []
    chosen_ids = []
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
            char_unique_id, char_id,  _ = chosen_line.split(' | ')
            chosen_unique_ids.append(int(char_unique_id))
            chosen_ids.append(int(char_id))

            # Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_all':
            # Get ID of chosen card to send to bandai
            for chosen_line in window['CARDS'].get_list_values():
                char_unique_id, char_id,  _ = chosen_line.split(' | ')
                chosen_unique_ids.append(int(char_unique_id))
                chosen_ids.append(int(char_id))

                # Chosen cards to display in lower box
                chosen_cards_to_display.append(chosen_line)

        if event == 'confirm_setup':
            break

        ###Re-populate cards to display, checking filter criteria
        cards_to_display[:] = []
        for char in cards_to_display_dicts:
            if int(char['UniqueID']) in chosen_unique_ids:
                continue
            cards_to_display.append(str(char['UniqueID']) + 
                                    ' | ' + str(char['ID']) + 
                                    ' | ' + str(char['Name']))

        window.find_element('CARDS').Update(values=cards_to_display)
        window.find_element('CARDS_CHOSEN').Update(values=chosen_cards_to_display)

    window.Close()

    noac = len(awaken_team(chosen_unique_ids, chosen_ids, master_cards))

    print(Back.LIGHTCYAN_EX + (Fore.GREEN if noac > 0 else Fore.RED) + f'Awakened {noac}/{len(chosen_unique_ids)} cards!')

    return 0 
