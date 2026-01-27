import json
import time
from random import randint
from typing import Optional

from colorama import Fore, Style

import config
import crypto
import models.game
import network
from commands import act
from services.stage import StageService
from services.account import AccountService

NAME = 'stage'
DESCRIPTION = 'Completes the given stage'
CONTEXT = [config.GameContext.GAME]
DLTM = 20


def run(stage_id: int, difficulty: Optional[int] = -1, kagi: Optional[int] = None):
    """Completes a stage with the given ID and difficulty."""

    # --- Convert CLI string arguments to integers safely ---
    try:
        stage_id = int(stage_id)
    except ValueError:
        print(Fore.RED + "[Stage] Invalid arguments: stage_id and difficulty must be numbers." + Style.RESET_ALL)
        return 0

    # --- Fetch quest info ---
    try:
        stage: Optional[models.game.Quests] = models.game.Quests.get_by_id(stage_id)
        lodfc = []
        sugorokus = list(models.game.SugorokuMaps.select().where(models.game.SugorokuMaps.quest_id == stage.id))
        for sug in sugorokus:
            lodfc.append(sug.difficulty)
        if not difficulty in lodfc:
            difficulty = lodfc[-1]
    except Exception as error:
        print(Fore.RED + f"[Stage] Error: {error}" + Style.RESET_ALL)
        print("[Stage] Does this quest exist?")
        return 0
    
    print(f"Begin stage: {stage.name} {stage_id} | Difficulty: {difficulty} Deck: {config.deck}")

    timer_start = int(round(time.time(), 0))

    friend = StageService.get_friend(stage_id, difficulty)
    # --- Get friend and sign info for starting the quest ---
    sign = StageService.get_sign(
        friend=friend,
        kagi=kagi,
        difficulty=difficulty,
        selected_team_num=config.deck,
    )

    enc_sign = crypto.encrypt_sign(json.dumps(sign))
    r = StageService.start_stage(stage_id, enc_sign)

    start_time = round(time.time())
    tts = randint(DLTM, DLTM + 9)
    time.sleep(tts)
    finish_time = time.time()

    # --- Handle possible API responses ---
    if not isinstance(r, dict):
        print(Fore.RED + f"[Stage] Unexpected response type: {type(r)}" + Style.RESET_ALL)
        return 0

    if r['result'] == 'success':
        dec_sign = crypto.decrypt_sign(r["sign"])
    elif r['result'] == 'low_stamina':
        if config.allow_stamina_refill:
            act.run()
            print("[Stage] Retrying after stamina refill...")
            return run(stage_id, kagi)
        else:
            print(Fore.RED + "[Stage] Stamina refill not allowed." + Style.RESET_ALL)
            return 0
    elif r['result'] == 'full_box':
        # Trigger auto cleanup hook if available
        try:
            from commands.autocleanup import auto_sell_junk
            print("[Stage] ⚠️ Card box full — running cleanup.")
            auto_sell_junk()
            return run(stage_id, kagi)
        except Exception as cleanup_error:
            print(Fore.RED + f"[Stage] Auto-cleanup failed: {cleanup_error}" + Style.RESET_ALL)
        return 0
    elif r['result'] == 'relogin':
        print(Fore.YELLOW + "[Stage] Token invalid — trying to re-login." + Style.RESET_ALL)
        config.game_account = AccountService.login(config.game_account)
        return 0
    else:
        return 0

    # --- Normal stage completion flow ---
    steps = []
    defeated = []
    for i in dec_sign["sugoroku"]["events"]:
        steps.append(i)
        event_data = dec_sign["sugoroku"]["events"][i]["content"]
        if "battle_info" in event_data:
            for j in event_data["battle_info"]:
                defeated.append(j["round_id"])

    damage = randint(499999, 1000000)

    # Hercule punching bag event high damage
    if str(stage_id)[:3] in ("711", "185", "186", "187"):
        damage = randint(100000000, 101000000)

    # Prepare finish payload
    sign = {
        "actual_steps": steps,
        "difficulty":difficulty,
        "elapsed_time": finish_time - start_time,
        "energy_ball_counts_in_boss_battle": [4, 6, 0, 6, 4, 3, 0, 0, 0, 0, 0, 0, 0],
        "has_player_been_taken_damage": False,
        "is_cheat_user": False,
        "is_cleared": True,
        "is_defeated_boss": True,
        "is_player_special_attack_only": True,
        "max_damage_to_boss": damage,
        "min_turn_in_boss_battle": len(defeated),
        "passed_round_ids": defeated,
        "quest_finished_at_ms": finish_time,
        "quest_started_at_ms": start_time,
        "steps": steps,
        "token": dec_sign["token"],
    }

    enc_sign = crypto.encrypt_sign(json.dumps(sign))
    r = network.post_quests_sugoroku_finish(stage_id, enc_sign)

    if "sign" in r:
        dcn = crypto.decrypt_sign(r["sign"])
        StageService.print_rewards(dcn)

    timer_total = int(round(time.time(), 0)) - timer_start
    print(Fore.GREEN + Style.BRIGHT + f"Completed stage {stage_id} in {timer_total} seconds" + Style.RESET_ALL)

    return 1
