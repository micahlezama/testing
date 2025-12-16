import json
import time
import traceback
from random import randint
from colorama import Fore

import config
import crypto
import models.game
import network


NAME = "eza farm"
DESCRIPTION = "Completes all Extreme Z-Awakenings (Z-Battles) up to level 31."
CONTEXT = [config.GameContext.GAME]
DLTM = 20  # seconds between runs


# ======================================================
# Get supporter from /z_battles/<id>/supporters
# ======================================================
def get_real_supporter(stage_id: int):
    try:
        print(Fore.YELLOW + f"🔍 Fetching supporter for Z-Battle {stage_id}…")
        data = network.get_zbattles_supporters(str(stage_id))

        if not data:
            print(Fore.RED + f"⚠️ No data returned from /z_battles/{stage_id}/supporters")
            return None
        if "error" in data:
            print(Fore.RED + f"⚠️ Error fetching supporter: {data['error']}")
            return None
        if "supporters" not in data or not data["supporters"]:
            print(Fore.YELLOW + "⚠️ Empty supporter list — skipping.")
            return None

        supporter = data["supporters"][0]
        print(Fore.CYAN + f"👥 Using supporter '{supporter.get('owner_name', 'Unknown')}' (Card ID {supporter.get('card_id')})")
        return supporter

    except Exception as e:
        print(Fore.RED + f"❌ Exception while fetching supporter: {e}")
        traceback.print_exc()
        return None


# ======================================================
# Main farming loop
# ======================================================
def run():
    try:
        zbattle_models = ["ZBattleStages", "ZBattles", "ZBattle", "ZBattleEvents"]
        zbattles = None
        for name in zbattle_models:
            if hasattr(models.game, name):
                zbattles = list(getattr(models.game, name).select())
                break

        if not zbattles:
            print(Fore.RED + "❌ No Z-Battle data model found in models.game.")
            return

        total = len(zbattles)
        print(Fore.CYAN + f"\n🔁 Found {total} EZA stages to run...\n")

        for eza_index, zb in enumerate(zbattles, start=1):
            stage_id = int(getattr(zb, "id", 0))
            if not stage_id:
                print(Fore.RED + f"⚠️ Invalid stage_id for EZA {eza_index}")
                continue

            print(Fore.MAGENTA + f"\n💥 EZA {eza_index}/{total}: Stage ID {stage_id}")

            supporter = get_real_supporter(stage_id)
            if not supporter:
                print(Fore.YELLOW + f"⚠️ Skipping EZA {stage_id} — no supporter found.")
                continue

            # Run all 31 levels
            for level in range(1, 32):
                try:
                    print(Fore.YELLOW + f"➡️ Starting EZA {stage_id} Level {level}…")

                    # ==========================
                    # 1️⃣ Start payload
                    # ==========================
                    start_payload = {
                        "z_battle_id": stage_id,
                        "level": level,
                        "selected_team_num": config.deck,
                        "is_supporter_selected": True,
                        "supporter_card_caches": [supporter],
                    }

                    print(Fore.LIGHTBLACK_EX + "[DEBUG] Start sign (before encryption):")
                    print(json.dumps(start_payload, indent=2))

                    enc_sign = crypto.encrypt_sign(json.dumps(start_payload))
                    r_start = network.post_zbattles_start(str(stage_id), enc_sign)
                    print(Fore.LIGHTBLACK_EX + f"[DEBUG] Start response: {r_start}")

                    if "error" in r_start:
                        code = r_start["error"].get("code")
                        print(Fore.RED + f"❌ Start error ({code})")
                        if code in (
                            "open_ssl/cipher/cipher_error",
                            "argument_error",
                            "not_exist_supporter_card_caches",
                        ):
                            print(Fore.YELLOW + f"⚠️ Skipping Stage {stage_id} Level {level}.")
                            break
                        continue

                    dec_sign = crypto.decrypt_sign(r_start["sign"])
                    token = dec_sign.get("token")
                    if not token:
                        print(Fore.RED + "⚠️ Missing token in start response.")
                        continue

                    print(Fore.GREEN + f"✅ Started EZA {stage_id} Level {level}")
                    print(Fore.BLUE + f"⏳ Waiting {DLTM} seconds before finishing…")

                    start_time = round(time.time())
                    time.sleep(DLTM)
                    finish_time = round(time.time())

                    # ==========================
                    # 2️⃣ Finish payload
                    # ==========================
                    finish_payload = {
                        "elapsed_time": finish_time - start_time,
                        "is_cleared": True,
                        "level": level,
                        "token": token,
                        "used_items": [],
                        "z_battle_started_at_ms": start_time * 1000,
                        "z_battle_finished_at_ms": finish_time * 1000,
                        "max_damage_to_boss": randint(400000, 900000),
                    }

                    print(Fore.LIGHTBLACK_EX + "[DEBUG] Finish sign (before encryption):")
                    print(json.dumps(finish_payload, indent=2))

                    enc_finish_sign = crypto.encrypt_sign(json.dumps(finish_payload))
                    r_finish = network.post_zbattles_finish(
                        str(stage_id),
                        finish_payload["elapsed_time"],
                        finish_payload["is_cleared"],
                        finish_payload["level"],
                        "s",
                        "t",
                        finish_payload["token"],
                        finish_payload["used_items"],
                        finish_payload["z_battle_finished_at_ms"],
                        finish_payload["z_battle_started_at_ms"],
                        None,
                    )

                    print(Fore.LIGHTBLACK_EX + f"[DEBUG] Finish response: {r_finish}")

                    if "error" in r_finish:
                        print(Fore.RED + f"❌ Finish error: {r_finish['error']}")
                        continue

                    print(Fore.GREEN + f"✅ Completed Stage {level}/31 of EZA {stage_id}")
                    time.sleep(DLTM)

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
