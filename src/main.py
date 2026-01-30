import requests
from colorama import Fore, init

import cli
import config
from classes.Game import GameEnvironment

init(autoreset=True)


def check_servers(env: GameEnvironment):
    print('Checking servers...')
    try:
        url = env.url + '/ping'
        headers = {
            'X-Platform': 'android',
            'X-ClientVersion': env.version_code,
            'X-Language': 'en',
            'X-UserID': '////'
        }
        r = requests.get(url, data=None, headers=headers)
        store = r.json()
        print(store)
        if 'error' in store:
            print(Fore.RED + '[' + env.name + ' server] ' + str(store['error']))
            return False
    except:
        print(Fore.RED + '[' + env.name + ' server] can\'t connect.')
        return False
    return True


def main():
    if not check_servers(config.game_env):
        print(Fore.RED + 'press ENTER to close...')
        input()
        exit()

    # ================================
    # UNCRASHABLE MENU LOOP
    # ================================
    while True:
        try:
            cli.run()   # your menu system
        except KeyboardInterrupt:
            print(Fore.RED + "\n⛔ Cancelled — returning to menu...\n")
            # loop continues, menu restarts
            continue
        except Exception as e:
            print(Fore.RED + f"\n💥 Unexpected error in menu: {e}\n")
            continue


if __name__ == "__main__":
    main()
