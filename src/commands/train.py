import FreeSimpleGUI as sg
from colorama import Fore, Style, Back

import config
import network

from utils.dbutils import cards_xptolv, item_exp, card_name, card_awakened, card_level
from models import game


NAME = 'train'
DESCRIPTION = 'Select characters to train'
CONTEXT = [config.GameContext.GAME]

def card_curexp(louc, cui):
    for ucard in louc:
        if ucard['id'] == cui:
            return ucard['exp']
    return 0

def add_exptotitems(louti, sort):
    loutiwe = []
    for i, ti in enumerate(louti):
        tid = ti['training_item_id']
        loutiwe.append(ti)
        loutiwe[i]['xp'] = item_exp(tid) 

    if sort:
        return list(sorted(loutiwe, key=lambda x: x['xp'] * (10 if x['quantity'] > 10 else x['quantity']), reverse=True))
    else:
        return loutiwe

def select_titems(exp, louti):
    loutiwe = add_exptotitems(louti, sort=True)
    sit = [] 
    for i, ti in enumerate(loutiwe):
        if len(sit) == 5:
            break
        quan = ti['quantity']
        quan = 10 if quan > 10 else quan
        mxexp = quan * ti['xp']
        if exp > 0:
            ntu = quan if mxexp < exp else round(exp / ti['xp'])
            if ntu == 0:
                continue
            xpgnd = ntu * ti['xp']
            exp -= xpgnd
            sit.append({
                'item_id':ti['training_item_id'],
                'quantity':ntu
            })
        else:
            return 0, sit 
    return exp, sit

def sort_texp(cidld):
    def aux_xp(cid):
        locuixp = cidld[cid]
        xp = locuixp[0][1]
        noc = len(locuixp) if len(locuixp) < 10 else 10
        return xp * noc

    return cidld, list(sorted(cidld.keys(), key=lambda k: aux_xp(k), reverse=True))

def group_cid(louc):
    cidld = {} 
    for ucard in louc:
        card = game.Cards.get_by_id(ucard['card_id'])
        cid = int(card.id)
        nad = (ucard['id'], card.training_exp if card.rarity == 0 else 0)
        if cid in cidld:
            cidld[cid].append(nad)
        else:
            cidld[cid] = [nad,]
    return cidld

def select_tcuis(exp, louc):
    lts = []
    cidld, sok = sort_texp(group_cid(louc))
    for k in sok:
        if len(lts) == 5:
            break
        dta = {'ids':[]}
        noc = 0
        for cui, xp in cidld[k]:
            if noc == 20:
                break
            if exp > 0:
                dta['ids'].append(cui)
                exp -= xp
                noc += 1
        if len(dta['ids']):
            lts.append(dta)

    return exp, lts

def train_card(cui, stis, stcs):
    tdata = {"item_cards": [],
            "training_field_id": 1,
            "training_items": stis,
            "user_cards": stcs} 
    return network.put_train(cui, tdata)

def train_team(locui:list[int], loci: list[int], ucards: list, custom_levels=[], skip_awakened=False):
    """
    Try to train all cards given
    
    :param louci: list of cards unique ids(network)
    :param loci:  list of cards ids(database)
    """
    notc = 0
    louti = network.get_train_items()['training_items']
    locxplv = cards_xptolv(loci, custom_levels)
    for i in range(len(locui)):
        cui = locui[i] 
        if skip_awakened and card_awakened(loci[i]):
            print(Fore.YELLOW + f'Card {cui} | {card_name(loci[i])} already awakened, skipping training...')
            notc += 1
            continue
        crnxp = card_curexp(ucards, cui)
        xptolv = locxplv[i]
        rmxp = xptolv - crnxp
        if rmxp <= 0:
            print(Fore.GREEN + f'Card {cui} | {card_name(loci[i])} Already trained!')
            notc += 1
            continue
        rmxp, stis = select_titems(rmxp, louti)
        if rmxp <= 0:
            r = train_card(cui, stis, [])
            louti = network.get_train_items()['training_items']
        else:
            rmxp, stcs = select_tcuis(rmxp, ucards)
            if rmxp <= 0:
                r = train_card(cui, stis, stcs)
                louti = network.get_train_items()['training_items']
                ucards = network.get_cards()['cards']
            else:
                r = False
                print(Fore.RED + f'Not enough resources to train {cui} | {card_name(loci[i])}')

        if not r or 'error' in r:
            if r != False:
                print(Fore.RED + f'Failed to train {cui} | {card_name(loci[i])}: {r}')
        else:
            crxp = r['card']['exp']
            crlv = card_level(loci[i], crxp)
            if crxp >= xptolv:
                pre = Fore.GREEN
                notc += 1
            else:
                pre = Fore.YELLOW
            print(pre + f'Card {cui} | {card_name(loci[i])} trained to level [{crlv}]')

    return notc

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
            'Level':card_level(card['card_id'], card['exp']),
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
                ' | ' + str(char['Name']) + ' | ' + str(char['Level']))


    ###Define window layout
    col1 = [[sg.Listbox(values=(cards_to_display), size=(60, 20), key='CARDS')],
            [sg.Text('Target level: '),
             sg.Spin([i for i in range(1, 150)], initial_value=80, size=(5, None), key='TARGET_LEVEL')],
            [sg.Button(button_text='Choose Card', key='choose_card'),
             sg.Button(button_text='Choose All', key='choose_all')],
            [sg.Listbox(values=([]), size=(60, 6), key='CARDS_CHOSEN')],
             [sg.Button(button_text='Confirm and train', key='confirm_setup')]]

    layout = [[sg.Column(col1)]]
    window = sg.Window('Train characters', grab_anywhere=True, keep_on_top=True).Layout(layout)

    ###Begin window loop
    chosen_unique_ids = []
    chosen_ids = []
    chosen_levels = []
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
            char_unique_id, char_id,  _, _ = chosen_line.split(' | ')
            chosen_unique_ids.append(int(char_unique_id))
            chosen_ids.append(int(char_id))
            chosen_levels.append(int(values['TARGET_LEVEL']))

            # Chosen cards to display in lower box
            chosen_cards_to_display.append(chosen_line)

        if event == 'choose_all':
            # Get ID of chosen card to send to bandai
            for chosen_line in window['CARDS'].get_list_values():
                char_unique_id, char_id,  _, _ = chosen_line.split(' | ')
                chosen_unique_ids.append(int(char_unique_id))
                chosen_ids.append(int(char_id))
                chosen_levels.append(int(values['TARGET_LEVEL']))

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
                ' | ' + str(char['Name']) + ' | ' + str(char['Level']))

        window.find_element('CARDS').Update(values=cards_to_display)
        window.find_element('CARDS_CHOSEN').Update(values=chosen_cards_to_display)

    window.Close()

    notc = train_team(chosen_unique_ids, chosen_ids, master_cards, chosen_levels)

    print(Back.LIGHTCYAN_EX + (Fore.GREEN if notc > 0 else Fore.RED) + f'Trained {notc}/{len(chosen_unique_ids)} cards!')

    return 0 
