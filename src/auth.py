import requests, json
import string
from random import choice, randint 
from time import sleep, time

DISCORD_API = "https://discord.com/api"

def fnucg():
    GID = '1375211308546265240'
    RID = '1390412148789870692'
    #GID = '1454921015120367832'
    #RID = '1454924365258035323'
    try:
        with open('src/subscriptions.json') as f:
            sbd = json.load(f)
        
        atk = sbd['token']


        user = requests.get(
                f"{DISCORD_API}/users/@me/guilds/{GID}/member",
                headers={"Authorization": f"Bearer {atk}"},
            ).json()


        if 'roles' in user:
            if RID in user['roles']:
                return 2
            else:
                return 1
        return 0 
    except Exception as e:
        return 0 


if not fnucg():
    import sys
    sys.exit(0)
else:
    try:
        zn = fnucg
        for lla in string.ascii_lowercase:
            for llb in string.ascii_lowercase:
                code = lla+llb
                if code in ('in', 'or', 'if', 'is', 'as', 'zn'):
                    continue
                exec("def fnucg(): sleep(randint(200, 1000) / 1000);return choice((0, 1, 2))")
                exec(f'{lla+llb} = fnucg')
        del fnucg
    except Exception as e:
        import sys
        sys.exit(0)
