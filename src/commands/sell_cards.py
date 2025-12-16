import network
import config
import sqlite3

# Command metadata
NAME = "sell cards"
DESCRIPTION = "Automatically sell low-rarity cards (N, R, SR) to clean up your box."
CONTEXT = [config.GameContext.GAME]


def run():
    print("[Sell Junk] Fetching your cards...")
    data = network.get_cards()
    if not data:
        print("No cards found.")
        return

    # Some API responses use { "cards": [...] } structure.
    cards = data.get("cards") if isinstance(data, dict) else data
    if not isinstance(cards, list):
        print("Unexpected card data format.")
        return

    sell_ids = []
    conn = sqlite3.connect(config.game_env.db_path)
    cursor = conn.cursor()

    # Loop through each card you own
    for card in cards:
        if not isinstance(card, dict):
            continue

        # Find the card's base rarity using local database
        cursor.execute("SELECT rarity FROM cards WHERE id = ?", (card["card_id"],))
        row = cursor.fetchone()

        # Add N, R, and SR cards to the sell list
        if row and row[0] in ["N", "R", "SR"]:
            sell_ids.append(card["id"])

    conn.close()

    # Nothing to sell? Exit early
    if not sell_ids:
        print("✅ No low-rarity cards found.")
        return

    print(f"[Sell Junk] Found {len(sell_ids)} low-rarity cards to sell (N/R/SR).")
    confirm = input("Are you sure you want to sell them all? (yes/no): ")
    if confirm.lower() != "yes":
        print("Cancelled.")
        return

    total_sold = 0
    total_zeni_gained = 0
    latest_balance = None

    # Sell in safe batches of 99
    for i in range(0, len(sell_ids), 99):
        batch = sell_ids[i:i + 99]
        print(f"Selling batch of {len(batch)} cards...")
        response = network.post_cards_sell(batch)

        if not response:
            print("⚠️ No response from server.")
            continue

        if "error" in response:
            print(f"❌ Error: {response['error'].get('code', 'unknown_error')}")
            continue

        # Track Zeni rewards
        gained = response.get("gain_zeni", 0)
        total_zeni_gained += gained
        latest_balance = response.get("zeni", latest_balance)
        total_sold += len(batch)

        print(f"✅ Sold {len(batch)} cards (+{gained:,} Zeni)")

    # Summary at the end
    print("\n===== Sell Summary =====")
    print(f"💰 Total cards sold: {total_sold}")
    print(f"💴 Total Zeni gained: {total_zeni_gained:,}")
    if latest_balance is not None:
        print(f"📦 New total Zeni: {latest_balance:,}")
    print("=========================")
    print("✅ All junk cards sold successfully!\n")
