from pathlib import Path

from colorama import Fore, Back, Style 

from classes.Game import GameAccount
from commands import load
import config
import network
import crypto


NAME = 'transfer'
DESCRIPTION = 'Transfer a google account'
CONTEXT = [config.GameContext.AUTH]

def run(save_as: str):
    print("[Transfer] Opening browser for authentication...") 
    token = network.get_gtoken()
    val_sign = network.post_auth_link(token, validate=True)['sign']
    print("[Transfer] Decrypting...") 
    val_res = crypto.decrypt_sign(val_sign)
    if val_res['is_platform_difference']:
        cp = config.game_platform.name
        if cp == config.ANDROID_PLATFORM.name:
            tp = config.IOS_PLATFORM.name
        else:
            tp = config.ANDROID_PLATFORM.name

        while True:
            ans = input(Fore.LIGHTRED_EX + 
                        f'[Transfer] Do you want to transfer from {cp} -> {tp}?')
            if ans == 'no':
                return
            elif ans == 'yes':
                break

    print("[Transfer] Requesting account transfer...")
    unique_id = crypto.generate_unique_id()
    sign = network.post_auth_link(token, uid=unique_id)['sign']
    res = crypto.decrypt_sign(sign)
    identifier = res['identifiers']

    print(Fore.WHITE + Back.GREEN +  Style.BRIGHT +
          "[Transfer] Transfer complete!")

    config.game_account = GameAccount(
        unique_id=unique_id,
        identifier=identifier
    )
    file_path = Path(config.ROOT_DIR, 'saves', save_as.strip() + '.json')
    config.game_account.to_file(file_path)

    load.run(save_as)
