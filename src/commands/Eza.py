import json
import time
import traceback
from random import randint
from colorama import Fore

import config
import crypto
from models import game
from commands.complete_zbattle_stage import clear_stage
import network


NAME = "eza farm"
DESCRIPTION = "Completes all Extreme Z-Awakenings (Z-Battles) up to level 31."
CONTEXT = [config.GameContext.GAME]


# ======================================================
# Helper: Check if an EZA is fully cleared
# ======================================================
def is_eza_cleared(stage_id, user_zbattles):
    # If server returned 0 or invalid data
    if not isinstance(user_zbattles, list):
        return False

    for zb in user_zbattles:
        if int(zb.get("z_battle_stage_id", -1)) == stage_id:
            max_lv = zb.get("max_clear_level", 0)
            return max_lv >= 31

    return False


# ======================================================
# Main farming loop
# ======================================================
def run():
    try:
        # Load all EZA stages from events
        lozs = network.get_events()['z_battle_stages']
        zbattles = [int(zs['id']) for zs in lozs]

        # Load user progress
        czbattles = network.get_user_zbattles()

        if not zbattles:
            print(Fore.RED + "❌ No Z-Battle data model found in models.game.")
            return

        total = len(zbattles)
        print(Fore.CYAN + f"\n🔁 Found {total} EZA stages to run...\n")

        # ======================================================
        # Loop through each EZA
        # ======================================================
        for eza_index, stage_id in enumerate(zbattles, start=1):

            print(Fore.MAGENTA + f"\n💥 EZA {eza_index}/{total}: Stage ID {stage_id}")

            # ---------------------------------------------------------
            # Skip if already cleared to level 31
            # ---------------------------------------------------------
            if is_eza_cleared(stage_id, czbattles):
                print(Fore.YELLOW + f"⏭️ Skipping EZA {stage_id} — already cleared to level 31.")
                continue

            # ---------------------------------------------------------
            # Determine starting level
            # ---------------------------------------------------------
            user_level = 1
            lvstp = 1

            for zb in czbattles:
                if int(zb.get("z_battle_stage_id", -1)) == stage_id:
                    max_lv = zb.get("max_clear_level", 0)

                    # Start at next level
                    user_level = max_lv + 1

                    # Special case: level 32 EZAs use 5-level jumps
                    if max_lv == 32:
                        lvstp = 5
                        user_level = lvstp

                    break

            print(Fore.CYAN + f"Current EZA Level: {user_level}")

            # ---------------------------------------------------------
            # Run levels up to 31
            # ---------------------------------------------------------
            for level in range(user_level, 32, lvstp):
                try:
                    print(Fore.YELLOW + f"➡️ Starting EZA {stage_id} Level {level}…")
                    clear_stage(stage_id, level)

                except Exception as inner_error:
                    print(Fore.RED + f"❌ Error on EZA {stage_id} Level {level}: {inner_error}")
                    traceback.print_exc()
                    continue

            print(Fore.CYAN + f"🏁 Finished all 31 stages of EZA {stage_id}")
            time.sleep(10)

        print(Fore.GREEN + "\n🎉 All EZAs completed successfully!\n")

    except KeyboardInterrupt:
        print(
            Fore.RED
            + "\n[EZA Farm] ❌ Interrupted by user — returning to main menu..."
        )
        return

    except Exception as e:
        print(Fore.RED + f"💥 Fatal error in EZA farm: {e}")
        traceback.print_exc()
