from typing import Optional
from colorama import Back, Fore, Style
from collections import defaultdict

import config
import models.game
import network
from services.stage import StageService

NAME = 'events'
DESCRIPTION = 'Browse and filter active events by type'
CONTEXT = [config.GameContext.GAME]


def categorize_event(area_name: str, quest_name: str) -> str:
    """Classify events by name pattern."""
    name = (area_name or quest_name or "").lower()

    if any(k in name for k in ["dokkan event", "transformation", "awakening", "awaken the power"]):
        return "Dokkan Events"
    elif any(k in name for k in ["super battle road", "sbr", "extreme sbr"]):
        return "Super Battle Road"
    elif any(k in name for k in ["category", "giant ape", "power", "only", "team", "bond"]):
        return "Category Battles"
    elif any(k in name for k in ["story", "saga", "movie", "gt", "heroes", "event"]):
        return "Story Events"
    else:
        return "Other Events"


def run(selected_group: Optional[str] = None):
    print(Fore.CYAN + "[Events] Fetching active events..." + Fore.RESET)
    events = network.get_events()

    if not isinstance(events, dict) or 'events' not in events:
        print(Fore.RED + "[Events] ❌ Failed to retrieve events." + Fore.RESET)
        if isinstance(events, dict) and 'error' in events:
            print(Fore.RED + f"API error: {events['error']}" + Fore.RESET)
        return

    grouped = defaultdict(list)

    for event in events['events']:
        area_id = event['id']

        # Try to get area name
        area_name = None
        try:
            area = models.game.Areas.get_by_id(area_id)
            if area:
                area_name = area.name.replace('\n', '')
        except Exception:
            pass

        # Fallbacks
        if not area_name:
            area_name = event.get('name')
        if not area_name and event['quests']:
            try:
                first_quest = models.game.Quests.get_by_id(event['quests'][0]['id'])
                area_name = first_quest.name.split(' - ')[0] if first_quest else "Unknown Quest Group"
            except Exception:
                area_name = "Unknown Quest Group"

        # Determine category
        first_quest_name = event['quests'][0].get('name', '') if event['quests'] else ""
        category = categorize_event(area_name, first_quest_name)

        # Collect quests
        quest_entries = []
        for quest in event['quests']:
            quest_id = quest['id']
            try:
                sugorokus = (
                    models.game.SugorokuMaps
                    .select()
                    .where(models.game.SugorokuMaps.quest_id == int(quest_id))
                )
            except Exception:
                continue

            difficulties = [StageService.get_difficulty_name(s.difficulty) for s in sugorokus]

            try:
                quest_obj = models.game.Quests.get_by_id(quest_id)
                quest_name = quest_obj.name if quest_obj else "Unknown Quest"
            except Exception:
                quest_name = "Unknown Quest"

            quest_entries.append((quest_id, quest_name, difficulties))

        grouped[category].append((area_id, area_name, quest_entries))

    # Category order
    ordered_categories = [
        "Dokkan Events",
        "Super Battle Road",
        "Category Battles",
        "Story Events",
        "Other Events"
    ]

    color_map = {
        "Dokkan Events": Fore.BLUE + Style.BRIGHT,
        "Super Battle Road": Fore.RED + Style.BRIGHT,
        "Category Battles": Fore.YELLOW + Style.BRIGHT,
        "Story Events": Fore.GREEN + Style.BRIGHT,
        "Other Events": Fore.WHITE + Style.BRIGHT
    }

    # ✅ Convert CLI arg safely to int
    if selected_group is not None:
        try:
            selected_group = int(selected_group)
        except ValueError:
            print(Fore.RED + f"Invalid input: '{selected_group}' (must be a number)." + Fore.RESET)
            return

    # If no selection → show menu
    if selected_group is None:
        print(Style.BRIGHT + "\nSelect event category:" + Style.RESET_ALL)
        for i, cat in enumerate(ordered_categories, start=1):
            print(f" {Fore.CYAN}{i}. {cat}{Fore.RESET}")
        print("\nType 'events [number]' to view that category.")
        return

    # Validate range
    if not (1 <= selected_group <= len(ordered_categories)):
        print(Fore.RED + "Invalid selection. Try again." + Fore.RESET)
        return

    # Print chosen group
    category = ordered_categories[selected_group - 1]
    events_to_show = grouped.get(category, [])
    color = color_map.get(category, Fore.WHITE)

    print("")
    print(color + f"===== {category.upper()} =====" + Style.RESET_ALL)
    if not events_to_show:
        print(Fore.YELLOW + "No events found for this category." + Fore.RESET)
        return

    for area_id, area_name, quests in events_to_show:
        print(Back.WHITE + Fore.BLACK + f"[{area_id}] {area_name}" + Style.RESET_ALL)
        for quest_id, quest_name, diffs in quests:
            diff_str = ", ".join([Fore.CYAN + d + Fore.RESET for d in diffs]) or "None"
            print(f"  {Fore.WHITE}{quest_id}{Fore.RESET} {Fore.GREEN}{quest_name}{Fore.RESET} [{diff_str}]")

    print(Fore.CYAN + f"\n[Events] ✅ Done showing {category}." + Fore.RESET)
