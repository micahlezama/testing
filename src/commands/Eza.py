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
# Main farming loop
# ======================================================
def run():
    try:
        lozs = network.get_events()['z_battle_stages']
        #zbattle_models = ["ZBattleStages", "ZBattles", "ZBattle", "ZBattleEvents"]
        zbattles = []
        for zs in lozs: 
            zbid = int(zs['id'])
            zbattles.append(zbid)
            #lozb = game.ZBattleCheckPoints.select().where(game.ZBattleCheckPoints.z_battle_stage_id == zbid)
            #for zb in lozb:
            #    print(zb.level)

        czbattles = network.get_user_zbattles()

        if not zbattles:
            print(Fore.RED + "❌ No Z-Battle data model found in models.game.")
            return

        total = len(zbattles)
        print(Fore.CYAN + f"\n🔁 Found {total} EZA stages to run...\n")

        for eza_index, zb in enumerate(zbattles, start=1):
            stage_id = zb
            if not stage_id:
                print(Fore.RED + f"⚠️ Invalid stage_id for EZA {eza_index}")
                continue

            print(Fore.MAGENTA + f"\n💥 EZA {eza_index}/{total}: Stage ID {stage_id}")

            # Get current zbattle level

            level = 1
            lvstp = 1
            for zbattle in czbattles:
                if int(zbattle['z_battle_stage_id']) == stage_id:
                    if zbattle['max_clear_level'] == 32:
                        lvstp = 5
                        level = lvstp 
                    else:
                        level = zbattle['max_clear_level'] + 1
                    print('Current EZA Level: ' + str(level))

            # Run all 31 levels
            for level in range(level, 32, lvstp):
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

    except Exception as e:
        print(Fore.RED + f"💥 Fatal error in EZA farm: {e}")
        traceback.print_exc()
