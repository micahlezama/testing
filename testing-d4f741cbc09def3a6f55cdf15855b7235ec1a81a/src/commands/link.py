from colorama import Fore, Style, Back

import config
import network


NAME = 'link'
DESCRIPTION = 'Link to a google account'
CONTEXT = [config.GameContext.GAME]
CATEGORY = 'Account Management'
def run():
    print("[Linking] Opening browser for authentiaction...")
    token = network.get_gtoken()
    network.post_link(token)
    print(Fore.WHITE + Back.BLUE +  Style.BRIGHT +
          "[Linking] Google account linked!")
