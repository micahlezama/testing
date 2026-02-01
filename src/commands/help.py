from inspect import getfullargspec

from colorama import Fore

import config
from services.command import CommandService

NAME = 'help'
DESCRIPTION = 'List of available commands'
CONTEXT = [config.GameContext.AUTH, config.GameContext.GAME]
CATEGORY = 'help'
def run():
    commands = CommandService.get_all()

    # Build category → list of commands
    sections = {}

    for command_name, command in commands.items():
        if config.game_context not in command.CONTEXT:
            continue

        category = getattr(command, 'CATEGORY', 'Other')

        if category not in sections:
            sections[category] = []

        sections[category].append(command)

    # Print each category
    for category, cmds in sections.items():
        print(Fore.CYAN + f"\n=== {category.upper()} ===" + Fore.RESET)

        for command in cmds:
            specs = getfullargspec(command.run)
            name = Fore.GREEN + command.NAME + Fore.RESET
            args = Fore.YELLOW + ' '.join('<' + arg + '>' for arg in specs.args) + Fore.RESET
            row = name + (' ' + args if specs.args else '') + ' ' + command.DESCRIPTION
            print(row)

    print('\nJoin our official ' + Fore.MAGENTA + 'Discord' + Fore.RESET + ' server: https://discord.gg/WWfXHDPAAm')
