import config
import models.game
from colorama import Fore, Back, Style
from commands import stage
from commands.autocleanup import auto_sell_junk
import network
from time import sleep

NAME = 'omega farm'
DESCRIPTION = 'Completes all quests, skipping cleared or unavailable ones automatically'
CONTEXT = [config.GameContext.GAME]


def run():
    print(Fore.YELLOW + "[Omega] Starting full quest farm..." + Fore.RESET)

    # === 1. Fetch cleared sugoroku map IDs from API ===
    cleared_data = network.get_quests()
    cleared_sugoroku_ids = {
        int(q["id"])
        for q in cleared_data.get("quests", [])
        if q.get("is_cleared")
    }

    print(
        Fore.CYAN
        + f"[Omega] Found {len(cleared_sugoroku_ids)} cleared difficulties from API."
        + Fore.RESET
    )

    # === 2. Fetch quests from DB (exclude tutorial) ===
    quests = list(
        models.game.Quests
        .select()
        .where(models.game.Quests.area_id > 1)
    )

    total = len(quests)
    print(Fore.CYAN + f"[Omega] Found {total} quests to process." + Fore.RESET)

    completed = 0
    skipped_cleared = 0
    skipped_unavailable = 0

    # === 3. Process quests ===
    for i, quest in enumerate(quests, start=1):
        quest_id = int(quest.id)

        # --- Fetch difficulties (sugoroku maps) ---
        sugorokus = list(
            models.game.SugorokuMaps
            .select()
            .where(models.game.SugorokuMaps.quest_id == quest_id)
        )

        for sugoroku in sugorokus:
            difficulty = sugoroku.difficulty

            # === Skip cleared difficulty ===
            if sugoroku.id in cleared_sugoroku_ids:
                skipped_cleared += 1
                print(
                    Fore.YELLOW
                    + f"[Omega] [SKIP] Quest {quest_id} "
                    + f"Difficulty {difficulty} already cleared."
                    + Fore.RESET
                )
                continue

            print(
                Fore.YELLOW
                + f"[Omega] Running quest {quest_id} - Difficulty {difficulty}"
                + Style.RESET_ALL
            )

            try:
                if stage.run(sugoroku.quest_id, difficulty):
                    completed += 1
            except Exception as e:
                print(f'Error happened while trying to clear stage ({e})')
                print(f'Retrying in 10 seconds...')
                sleep(10)

        # --- Progress ---
        print(
            Fore.WHITE
            + Back.BLUE
            + Style.BRIGHT
            + f"Progress: {i}/{total} ({round((i / total) * 100)}%)"
            + Style.RESET_ALL
        )

    # === 4. Summary ===
    print("\n" + Fore.CYAN + Style.BRIGHT + "====== Ω Summary ======" + Style.RESET_ALL)
    print(Fore.YELLOW + f"Total quests scanned: {total}" + Fore.RESET)
    print(Fore.YELLOW + f"Skipped (already cleared difficulties): {skipped_cleared}" + Fore.RESET)
    print(Fore.YELLOW + f"Skipped (unavailable): {skipped_unavailable}" + Fore.RESET)
    print(Fore.GREEN + f"Stages completed: {completed}" + Fore.RESET)
    print(Fore.CYAN + Style.BRIGHT + "========================" + Style.RESET_ALL)

    print(
        Fore.GREEN
        + Style.BRIGHT
        + "[Omega] ✅ Run complete — all available uncleared stages finished!"
        + Style.RESET_ALL
    )
