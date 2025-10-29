import network
import config

NAME = "sell cards"
DESCRIPTION = "Sell selected cards in batches of 99"
CONTEXT = [config.GameContext.GAME]

def run(card_list):
    # Handle case where the user passed a single ID (string)
    if isinstance(card_list, str):
        card_list = [card_list]

    # Convert all IDs to integers and skip invalid ones
    try:
        card_list = [int(x) for x in card_list if str(x).isdigit()]
    except ValueError:
        print("Invalid card IDs provided.")
        return

    if not card_list:
        print("No valid card IDs provided.")
        return

    cards_to_sell = []
    i = 0

    for card in card_list:
        i += 1
        cards_to_sell.append(card)

        # Sell cards in batches of 99 (API limit)
        if i == 99:
            r = network.post_cards_sell(cards_to_sell)
            print(f"Sold Cards x{len(cards_to_sell)}")
            _handle_sell_response(r)
            i = 0
            cards_to_sell[:] = []

    # Sell leftover cards (if any)
    if i != 0:
        r = network.post_cards_sell(cards_to_sell)
        print(f"Sold Cards x{len(cards_to_sell)}")
        _handle_sell_response(r)


def _handle_sell_response(response):
    """Handles API response and displays useful info."""
    if not response:
        print("⚠️ No response from server.")
        return

    # Handle API error codes
    if 'error' in response:
        print(f"❌ Error: {response['error'].get('code', 'unknown_error')}")
        return

    # Show success details
    gain_zeni = response.get('gain_zeni', 0)
    new_total = response.get('zeni', None)

    if gain_zeni or new_total:
        print(f"✅ Gained {gain_zeni:,} Zeni. New balance: {new_total:,}")
    else:
        print("✅ Cards sold successfully.")
