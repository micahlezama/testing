from typing import Optional
from colorama import Fore, Style
import config
import models.game
import network

NAME = 'cards'
DESCRIPTION = 'List your cards (filter by rarity or type, e.g. "cards lr" or "cards teq")'
CONTEXT = [config.GameContext.GAME]

_CARD_TYPES = ['AGL', 'TEQ', 'INT', 'STR', 'PHY']
_CARD_COLORS = {
    'AGL': Fore.BLUE,
    'TEQ': Fore.GREEN,
    'INT': Fore.MAGENTA,
    'STR': Fore.RED,
    'PHY': Fore.YELLOW
}

# Map rarity numbers to readable labels
_RARITY_MAP = {
    0: 'N',
    1: 'R',
    2: 'SR',
    3: 'SSR',
    4: 'UR',
    5: 'LR'
}

_RARITY_COLORS = {
    'N': Fore.WHITE,
    'R': Fore.CYAN,
    'SR': Fore.GREEN,
    'SSR': Fore.YELLOW,
    'UR': Fore.MAGENTA,
    'LR': Fore.RED + Style.BRIGHT
}


def run(filter_arg: Optional[str] = None):
    """List cards, optionally filtered by rarity (e.g., LR) or type (e.g., TEQ)."""
    res = network.get_cards()

    if 'cards' not in res:
        print(Fore.RED + "❌ Failed to fetch cards." + Fore.RESET)
        return

    cards = res['cards']

    # Normalize filter
    filter_arg = filter_arg.upper() if filter_arg else None

    count = 0
    for card in cards:
        card_id = card['card_id']

        db_card: Optional[models.game.Cards] = models.game.Cards.get_by_id(card_id)
        if not db_card:
            continue

        # Convert rarity number to text label
        rarity_value = db_card.rarity
        if isinstance(rarity_value, str) and rarity_value.isdigit():
            rarity_value = int(rarity_value)
        rarity = _RARITY_MAP.get(rarity_value, '??')

        # Determine card type (element)
        try:
            element_idx = int(str(db_card.element)[-1])
            element = _CARD_TYPES[element_idx]
        except Exception:
            element = "???"

        # Apply filters
        if filter_arg:
            if filter_arg in _RARITY_MAP.values() and rarity != filter_arg:
                continue
            if filter_arg in _CARD_TYPES and element != filter_arg:
                continue

        rarity_color = _RARITY_COLORS.get(rarity, Fore.WHITE)
        element_color = _CARD_COLORS.get(element, Fore.WHITE)

        favorite_star = '★' if card.get('is_favorite') else ' '
        print(
            f"{favorite_star} "
            f"{Fore.WHITE}{card_id}{Fore.RESET} "
            f"{Fore.LIGHTBLACK_EX}{card['id']}{Fore.RESET} "
            f"{element_color}[{element}]{Fore.RESET}"
            f"{rarity_color}[{rarity}]{Fore.RESET} "
            f"{Fore.CYAN}{db_card.name}{Fore.RESET}"
        )
        count += 1

    # Summary
    if filter_arg:
        print(Fore.YELLOW + f"\n[Cards] ✅ Displayed {count} {filter_arg} cards." + Fore.RESET)
    else:
        print(Fore.YELLOW + f"\n[Cards] ✅ Displayed {count} total cards." + Fore.RESET)
