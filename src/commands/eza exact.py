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


NAME = "eza exact"
DESCRIPTION = "Completes selected Extreme Z-Awakenings (Z-Battles) up to a chosen level."
CONTEXT = [config.GameContext.GAME]
CATEGORY = 'Zbattle'

def run():

    try:
        # Load all EZA stages from server
        lozs = network.get_events()['z_battle_stages']
        zbattles = [int(zs['id']) for zs in lozs]

        if not zbattles:
            print(Fore.RED + "❌ No Z-Battle data found.")
            return

        # ======================================================
        # 1. Show all EZAs to the user
        # ======================================================
        print(Fore.CYAN + "\nAvailable EZA Stages:\n")
        for idx, stage_id in enumerate(zbattles, start=1):
            print(f"{idx}) Stage ID {stage_id}")

        # ======================================================
        # 2. User selects which EZA to farm
        # ======================================================
        try:
            choice = input("\nEnter the number of the EZA you want to farm: ").strip()
        except KeyboardInterrupt:
            print(Fore.RED + "\n[EZA Exact] ❌ Cancelled — returning to main menu...")
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(zbattles)):
            print(Fore.RED + "❌ Invalid choice.")
            return

        stage_id = zbattles[int(choice) - 1]
        print(Fore.MAGENTA + f"\nSelected EZA Stage ID: {stage_id}")

        # ======================================================
        # 3. Get user's current progress for this EZA
        # ======================================================
        czbattles = network.get_user_zbattles()
        current_level = 1

        for zbattle in czbattles:
            if int(zbattle['z_battle_stage_id']) == stage_id:
                current_level = zbattle['max_clear_level'] + 1
                break

        print(Fore.YELLOW + f"Your current level for this EZA is: {current_level}")

        # ======================================================
        # 4. User chooses target level
        # ======================================================
        try:
            target_level = input("Enter the level you want to farm up to (max 999): ").strip()
        except KeyboardInterrupt:
            print(Fore.RED + "\n[EZA Exact] ❌ Cancelled — returning to main menu...")
            return

        if not target_level.isdigit():
            print(Fore.RED + "❌ Invalid level.")
            return

        target_level = int(target_level)

        if target_level < current_level or target_level > 999:
            print(Fore.RED + "❌ Target level must be between your current level and 999.")
            return

        print(Fore.CYAN + f"\nFarming EZA {stage_id} from level {current_level} → {target_level}\n")

        # ======================================================
        # 5. Run the levels
        # ======================================================
        try:
            for level in range(current_level, target_level + 1):
                try:
                    print(Fore.YELLOW + f"➡️ Starting Level {level}…")
                    clear_stage(stage_id, level)
                    time.sleep(1)

                except Exception as inner_error:
                    print(Fore.RED + f"❌ Error on Level {level}: {inner_error}")
                    traceback.print_exc()
                    continue

        except KeyboardInterrupt:
            print(Fore.RED + "\n[EZA Exact] ❌ Interrupted — returning to main menu...")
            return

        print(Fore.GREEN + f"\n🎉 Finished farming EZA {stage_id} up to level {target_level}!\n")

    except KeyboardInterrupt:
        print(Fore.RED + "\n[EZA Exact] ❌ Cancelled — returning to main menu...")
        return

    except Exception as e:
        print(Fore.RED + f"💥 Fatal error in EZA exact: {e}")
        traceback.print_exc()
