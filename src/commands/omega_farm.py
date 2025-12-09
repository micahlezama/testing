import config
import models.game
from colorama import Fore, Back, Style
from commands import stage
from commands.autocleanup import auto_sell_junk
import network

# Import StageService from the stage module
from commands.stage import StageService

NAME = 'omega farm'
DESCRIPTION = 'Completes all quests, skipping cleared or unavailable ones automatically'
CONTEXT = [config.GameContext.GAME]


def run():
    print(Fore.YELLOW + "[Omega] Starting full quest farm..." + Fore.RESET)

    # === 1. Fetch cleared quest data ===
    cleared_data = network.get_quests()
    cleared_ids = {int(q["id"]) for q in cleared_data.get("quests", []) if q.get("is_cleared")}
    print(Fore.CYAN + f"[Omega] Found {len(cleared_ids)} cleared stages from API." + Fore.RESET)

    # === 2. Fetch quests (excluding tutorial) ===
    quests = list(models.game.Quests.select().where(models.game.Quests.area_id > 1))
    total = len(quests)
    print(Fore.CYAN + f"[Omega] Found {total} quests to process." + Fore.RESET)

    i = 1
    total_skipped = 0
    total_completed = 0
    total_unavailable = 0

    # === 3. Iterate through all quests ===
    for quest in quests:
        sugorokus = list(models.game.SugorokuMaps.select().where(models.game.SugorokuMaps.quest_id == quest.id))

        for sugoroku in sugorokus:
            stage_id = int(sugoroku.id)

            # === Skip cleared quests ===
            if stage_id in cleared_ids:
                total_skipped += 1
                print(Fore.YELLOW + f"[Omega] [SKIP] Stage {stage_id} already cleared ({quest.name})." + Fore.RESET)
                continue

            # === Build sign for stage start ===
            friend = StageService.get_friend(stage_id, sugoroku.difficulty)
            sign = StageService.get_sign(friend, None, sugoroku.difficulty, selected_team_num=1)
            if not sign:
                print(Fore.RED + f"[Omega] ⚠️ Could not build sign for stage {stage_id}, skipping." + Fore.RESET)
                continue

            # === Try to start stage (handles unavailable_quest) ===
            start_res = StageService.start_stage(stage_id, sign)
            if isinstance(start_res, dict) and start_res.get("skip") == "unavailable_quest":
                print(Fore.YELLOW + f"[Omega] ⚠️ Quest {stage_id} unavailable — skipping." + Style.RESET_ALL)
                total_unavailable += 1
                continue

            # === Run stage normally ===
            print(
                Fore.YELLOW
                + f"[Omega] Running quest {quest.id} (Area {quest.area_id}) - Difficulty {sugoroku.difficulty}"
                + Style.RESET_ALL
            )
            res = stage.run(quest.id, sugoroku.difficulty)

            # === Handle card box full ===
            if isinstance(res, dict) and "error" in res:
                err_code = res["error"].get("code", "")
                if err_code == "the_number_of_cards_must_be_less_than_or_equal_to_the_capacity":
                    print(Fore.RED + "[Omega] ⚠️ Card box full — triggering auto cleanup." + Fore.RESET)
                    auto_sell_junk()

                    print("[Omega] Retrying quest after cleanup...")
                    retry_res = stage.run(quest.id, sugoroku.difficulty)

                    if (
                        isinstance(retry_res, dict)
                        and "error" in retry_res
                        and retry_res["error"].get("code") == "the_number_of_cards_must_be_less_than_or_equal_to_the_capacity"
                    ):
                        print(Fore.RED + "[Omega] ⚠️ Cleanup failed to free enough space — stopping run." + Style.RESET_ALL)
                        return

            total_completed += 1

        # === Quest progress ===
        print(
            Fore.WHITE
            + Back.BLUE
            + Style.BRIGHT
            + f"Completion of quest: {i}/{total} ({round((i / total) * 100)}%)"
            + Style.RESET_ALL
        )
        i += 1

    # === 4. Final summary ===
    print("\n" + Fore.CYAN + Style.BRIGHT + "====== Ω Summary ======" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Total quests scanned: {total}" + Fore.RESET)
    print(Fore.YELLOW + f"Total cleared stages skipped: {total_skipped}" + Fore.RESET)
    print(Fore.YELLOW + f"Total unavailable stages skipped: {total_unavailable}" + Fore.RESET)
    print(Fore.GREEN + f"Total stages completed: {total_completed}" + Fore.RESET)
    print(Fore.CYAN + Style.BRIGHT + "========================" + Style.RESET_ALL)

    print(Fore.GREEN + Style.BRIGHT + "[Omega] ✅ Run complete — all uncleared and available stages finished!" + Style.RESET_ALL)
