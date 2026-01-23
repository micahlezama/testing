import json
import time
import traceback
from colorama import Fore

import config
from commands.complete_zbattle_stage import clear_stage
import network


NAME = "zeni"
DESCRIPTION = "Farms Zeni by clearing EZA Stage 1 up to level 31 if needed, then continues for statue farming."
CONTEXT = [config.GameContext.GAME]


def run():
    try:
        # Load all EZA stages from server
        lozs = network.get_events()['z_battle_stages']
        zbattles = [int(zs['id']) for zs in lozs]

        if not zbattles:
            print(Fore.RED + "❌ No Z-Battle data found.")
            return

        # Always use the FIRST EZA stage
        stage_id = zbattles[0]
        print(Fore.MAGENTA + f"\nUsing EZA Stage ID {stage_id} for Zeni farming.")

        # ======================================================
        # Get user's current progress for this EZA
        # ======================================================
        czbattles = network.get_user_zbattles()
        current_level = 1

        for zbattle in czbattles:
            if int(zbattle['z_battle_stage_id']) == stage_id:
                current_level = zbattle['max_clear_level'] + 1
                break

        print(Fore.YELLOW + f"Your current level for this EZA is: {current_level}")

        # ======================================================
        # If below 31 → clear up to 31
        # ======================================================
        if current_level < 31:
            print(Fore.CYAN + f"\nClearing up to level 31 first (current: {current_level})...\n")

            for level in range(current_level, 32):
                try:
                    print(Fore.YELLOW + f"➡️ Clearing Level {level}…")
                    clear_stage(stage_id, level)
                    time.sleep(1)
                except Exception as inner_error:
                    print(Fore.RED + f"❌ Error on Level {level}: {inner_error}")
                    traceback.print_exc()
                    continue

            print(Fore.GREEN + "\n✅ Reached Level 31!\n")
            current_level = 31

        # ======================================================
        # Ask user how many statues they want
        # ======================================================
        amount = input("How many Hercule statues do you want to farm? ").strip()

        if not amount.isdigit():
            print(Fore.RED + "❌ Invalid number.")
            return

        amount = int(amount)

        if amount <= 0:
            print(Fore.RED + "❌ Amount must be greater than 0.")
            return

        # ======================================================
        # If current level is ABOVE 31, start from that level
        # ======================================================
        start_level = current_level
        end_level = start_level + amount - 1

        print(Fore.CYAN + f"\nFarming {amount} statues starting from level {start_level} → {end_level}...\n")

        # ======================================================
        # Farming loop
        # ======================================================
        for level in range(start_level, end_level + 1):
            try:
                print(Fore.YELLOW + f"➡️ Farming Level {level}…")
                clear_stage(stage_id, level)
                time.sleep(1)
            except Exception as inner_error:
                print(Fore.RED + f"❌ Error on Level {level}: {inner_error}")
                traceback.print_exc()
                continue

        print(Fore.GREEN + f"\n🎉 Finished farming {amount} statues (Levels {start_level} → {end_level})!\n")

    except Exception as e:
        print(Fore.RED + f"💥 Fatal error in Zeni farm: {e}")
        traceback.print_exc()
