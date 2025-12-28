import network
import models.game
import time

from config import GameContext

NAME = 'auto-sell'
DESCRIPTION = 'Auto-sell junk'
CONTEXT = [GameContext.GAME]

def run():
    """Automatically sells low-rarity cards (N and R)."""
    print("[AutoCleanup] Starting automatic card cleanup...")

    try:
        res = network.get_cards()
    except Exception as e:
        print(f"[AutoCleanup][ERROR] Failed to fetch cards: {e}")
        return

    if "cards" not in res:
        print("[AutoCleanup][WARN] No cards key found in response.")
        return

    cards = res["cards"]
    print(f"[AutoCleanup] Retrieved {len(cards)} total cards from server.")

    junk_cards = []
    rarity_map = {0: "N", 1: "R", 2: "SR", 3: "SSR", 4: "UR", 5: "LR"}

    for card in cards:
        try:
            db_card = models.game.Cards.get_by_id(card["card_id"])
            rarity_value = getattr(db_card, "rarity", None)

            # convert numeric rarity to readable form
            if isinstance(rarity_value, int):
                rarity_name = rarity_map.get(rarity_value, "?")
            else:
                rarity_name = str(rarity_value).upper()

        except Exception as e:
            rarity_name = "?"
            print(f"[AutoCleanup][WARN] Failed to read card rarity: {e}")
            continue

        # check if junk
        if rarity_name in ["N", "R"]:
            junk_cards.append({
                "id": card["id"],
                "name": db_card.name if db_card else "?",
                "rarity": rarity_name
            })

    print(f"[AutoCleanup] Identified {len(junk_cards)} junk cards (N/R).")

    if not junk_cards:
        print("[AutoCleanup] No junk cards to sell. Cleanup skipped.")
        return

    # Log a few junk cards for confirmation
    for c in junk_cards[:5]:
        print(f"[AutoCleanup] Example junk: [{c['rarity']}] {c['name']} (ID: {c['id']})")

    # Sell in safe batches of 99
    batch_size = 99
    for i in range(0, len(junk_cards), batch_size):
        batch = junk_cards[i:i + batch_size]
        card_ids = [c["id"] for c in batch]

        print(f"[AutoCleanup] Selling batch {i//batch_size + 1}: {len(batch)} cards...")
        res = network.post_cards_sell(card_ids)
        print(f"[AutoCleanup] Sell result: {res}")
        time.sleep(1)

    print("[AutoCleanup] ✅ Cleanup complete.")

auto_sell_junk = run
