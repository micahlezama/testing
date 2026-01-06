import json
import urllib.parse
import time
from typing import Optional, Any

import requests
from colorama import Fore
from requests import Response

import config
import crypto
from classes.Game import GamePlatform

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
import selenium.webdriver.support.ui as ui

def __generate_headers(
        method: str,
        endpoint: str,
        platform: GamePlatform = config.game_platform,
        client_version: str = config.game_env.version_code,
        language: str = 'en',
        asset_version: str = '////',
        database_version: str = '////'
) -> "dict[str: any]":
    return {
        'User-Agent': platform.user_agent,
        'Accept': '*/*',
        'Authorization': 'Bearer ' + config.game_account.access_token,
        'Content-type': 'application/json',
        'X-Platform': platform.name,
        'X-AssetVersion': asset_version,
        'X-DatabaseVersion': database_version,
        'X-ClientVersion': client_version,
        'X-Language': language
    }


def __purge_none(data: Optional[dict] = None) -> Optional[dict]:
    if data is None: return data
    _copy = data.copy()

    for key in data:
        if type(data[key]) is dict:
            _copy[key] = __purge_none(_copy[key])
        if _copy[key] is None:
            _copy.pop(key)

    return _copy if len(_copy) > 0 else None


def __print_response(res: Response):
    status_color = Fore.RED
    if 100 <= res.status_code <= 199: status_color = Fore.BLUE
    elif 200 <= res.status_code <= 299: status_color = Fore.GREEN
    elif 300 <= res.status_code <= 399: status_color = Fore.YELLOW
    show_content = False
    status_code = '[' + status_color + str(res.status_code) + Fore.RESET + ']'
    url = Fore.GREEN + res.url + Fore.RESET

    print(status_code + ' ' + res.request.method + ' ' + url)
    if show_content: print(res.text)


def __get(endpoint: str, params: Optional[Any] = None):
    params = __purge_none(params)
    if params is not None:
        endpoint = endpoint + '?' + urllib.parse.urlencode(params)

    url = config.game_env.url + endpoint
    headers = __generate_headers('GET', endpoint)
    res = requests.get(url, headers=headers, timeout=20)
    #print(res.json())
    return res.json() if res.status_code != 204 else None


def __put(endpoint: str, data: Optional[dict[str, Any]] = None):
    headers = __generate_headers('PUT', endpoint)
    url = config.game_env.url + endpoint
    data = __purge_none(data)
    res = requests.put(url, headers=headers, data=json.dumps(data) if data is not None else None, timeout=20)
    
    return res.json() if res.status_code != 204 else None


def __post(endpoint: str, data: Optional[dict[str, Any]] = None):
    headers = __generate_headers('POST', endpoint)
    url = config.game_env.url + endpoint
    data = __purge_none(data)
    res = requests.post(url, headers=headers, data=json.dumps(data) if data is not None else None, timeout=20)
    return res.json() if res.status_code != 204 else None


def get_user():
    return __get('/user')


def get_user_areas():
    return __get('/user_areas')

def get_user_zbattles():
    r = get_user_areas()
    if 'user_z_battles' in r:
        zbattles = r['user_z_battles']
        if zbattles == []:
            zbattles = 0
    else:
        zbattles = 0
    
    return zbattles

def get_events():
    return __get('/events')


def get_eventkagi_items():
    return __get('/eventkagi_items')


def get_cards():
    return __get('/cards')


def get_client_assets_database():
    return __get('/client_assets/database')


def get_gifts():
    return __get('/gifts')


def get_missions():
    return __get('/missions')


def get_awakening_items():
    return __get('/awakening_items')


def get_gashas():
    return __get('/gashas')


def get_support_leaders():
    return __get('/support_leaders')


def get_teams():
    return __get('/teams')


def get_dragonball_sets():
    return __get('/dragonball_sets')


def get_dragonball_sets_wishes(set: str):
    return __get('/dragonball_sets/' + set + '/wishes')


def get_resources_home(
    apologies: bool = False,
    banners: bool = False,
    bonus_schedules: bool = False,
    budokai: bool = False,
    dragonball_sets: bool = False,
    gifts: bool = False,
    login_bonuses: bool = False,
    missions: bool = False,
    random_login_bonuses: bool = False,
    rmbattles: bool = False,
    user_subscription: bool = False,
    comeback_campaigns: bool = False,
): return __get('/resources/home', {
    'apologies': str(apologies).lower(),
    'banners': str(banners).lower(),
    'bonus_schedules': str(bonus_schedules).lower(),
    'budokai': str(budokai).lower(),
    'dragonball_sets': str(dragonball_sets).lower(),
    'gifts': str(gifts).lower(),
    'login_bonuses': str(login_bonuses).lower(),
    'missions': str(missions).lower(),
    'random_login_bonuses': str(random_login_bonuses).lower(),
    'rmbattles': str(rmbattles).lower(),
    'user_subscription': str(user_subscription).lower(),
    'comeback_campaigns': str(comeback_campaigns).lower(),
})


def get_resources_login(
        act_items: bool = False,
        announcements: bool = False,
        awakening_items: bool = False,
        budokai: bool = False,
        card_sticker_items: bool = False,
        card_tags: bool = False,
        cards: bool = False,
        chain_battles: bool = False,
        comeback_campaigns: bool = False,
        cooperation_campaigns: bool = False,
        dragonball_sets: bool = False,
        equipment_skill_items: bool = False,
        eventkagi_items: bool = False,
        friendships: bool = False,
        gashas: bool = False,
        gifts: bool = False,
        joint_campaigns: bool = False,
        login_bonuses: bool = False,
        login_movies: bool = False,
        login_popups: bool = False,
        missions: bool = False,
        potential_items: bool = False,
        rmbattles: bool = False,
        sd_battle: bool = False,
        sd_characters: bool = False,
        sd_packs: bool = False,
        secret_treasure_boxes: bool = False,
        shops_treasure_items: bool = False,
        sns_campaign: bool = False,
        support_films: bool = False,
        support_items: bool = False,
        support_leaders: bool = False,
        support_memories: bool = False,
        teams: bool = False,
        training_fields: bool = False,
        training_items: bool = False,
        treasure_items: bool = False,
        user_areas: bool = False,
        user_card_updated_at: bool = False,
        user_subscription: bool = False,
        wallpaper_items: bool = False,
        special_items: bool = False
): return __get('/resources/login', {
    'potential_items': str(potential_items).lower(),
    'training_items': str(training_items).lower(),
    'support_items': str(support_items).lower(),
    'treasure_items': str(treasure_items).lower(),
    'special_items': str(special_items).lower(),
    'sd/battle': str(sd_battle).lower(),
    'sd/characters': str(sd_characters).lower(),
    'sd/packs': str(sd_packs).lower(),
    'shop/treasure/items': str(shops_treasure_items).lower(),
    'user_areas': str(user_areas).lower(),
    'user_card_updated_at': str(user_card_updated_at).lower(),
    'user_subscription': str(user_subscription).lower(),
    'wallpaper_items': str(wallpaper_items).lower(),
    'support_leaders': str(support_leaders).lower(),
    'support_memories': str(support_memories).lower(),
    'teams': str(teams).lower(),
    'training_fields': str(training_fields).lower(),
    'sns_campaign': str(sns_campaign).lower(),
    'support_films': str(support_films).lower(),
    'secret_treasure_boxes': str(secret_treasure_boxes).lower(),
    'rmbattles': str(rmbattles).lower(),
    'act_items': str(act_items).lower(),
    'announcements': str(announcements).lower(),
    'awakening_items': str(awakening_items).lower(),
    'budokai': str(budokai).lower(),
    'card_sticker_items': str(card_sticker_items).lower(),
    'card_tags': str(card_tags).lower(),
    'cards': str(cards).lower(),
    'chain_battles': str(chain_battles).lower(),
    'comeback_campaigns': str(comeback_campaigns).lower(),
    'cooperation_campaigns': str(cooperation_campaigns).lower(),
    'dragonball_sets': str(dragonball_sets).lower(),
    'equipment_skill_items': str(equipment_skill_items).lower(),
    'eventkagi_items': str(eventkagi_items).lower(),
    'friendships': str(friendships).lower(),
    'gashas': str(gashas).lower(),
    'gifts': str(gifts).lower(),
    'joint_campaigns': str(joint_campaigns).lower(),
    'login_bonuses': str(login_bonuses).lower(),
    'login_movies': str(login_movies).lower(),
    'login_popups': str(login_popups).lower(),
    'missions': str(missions).lower(),
})

def get_quests_supporters(stage_id: int, difficulty: int, team_num: int):
    params = {'difficulty': difficulty, 'force_update': '', 'team_num': team_num}
    r = __get(f'/quests/{stage_id}/briefing', params)

    # Normalize structure so StageService never crashes
    if "error" in r:
        return {
            "supporters": [],
            "cpu_supporters": {},
            "error": r["error"]
        }

    if "supporters" not in r:
        r["supporters"] = []

    if "cpu_supporters" not in r:
        r["cpu_supporters"] = {}

    return r

def get_quests():
    data = __get('/user_areas')
    quests = []
    for area in data.get("user_areas", []):
        for m in area.get("user_sugoroku_maps", []):
            quests.append({
                "id": m["sugoroku_map_id"],
                "is_cleared": m.get("cleared_count", 0) > 0
            })
    return {"quests": quests}

def get_rmbattles(clash_id: str):
    return __get('/rmbattles/' + clash_id)


def get_rmbattles_available_user_cards():
    return __get('/rmbattles/available_user_cards')


def get_rmbattles_teams(team_id: str):
    return __get('/rmbattles/teams/' + team_id)


def get_zbattles_supporters(stage_id: str, level: int, team_num: int):
    params = {'level': level, 'force_update':'', 'team_num': team_num}
    return __get('/z_battles/' + stage_id + '/briefing', params=params)


def get_item_reverse_resolutions_awakening_items():
    return __get('/item_reverse_resolutions/awakening_items')


def put_user(
        name: Optional[str] = None,
        is_ondemand: Optional[bool] = None
): return __put('/user', {
    'user': {
        'name': name,
        'is_ondemand': is_ondemand
    }
})


def put_user_recover_act_with_stones():
    return __put('/user/recover_act_with_stone')


def put_support_leaders(support_leader_ids: list[int]):
    return __put('/support_leaders', {
        'support_leader_ids': support_leader_ids
    })


def put_rmbattles_team(team_index: str, user_card_ids: list):
    return __put('/rmbattles/teams/' + team_index, {
        'user_card_ids': user_card_ids
    })


def put_tutorial_finish():
    return __put('/tutorial/finish')


def put_tutorial(progress: int):
    return __put('/tutorial', {'progress': progress})


def put_apologies_accept():
    return __put('/apologies/accept')


def put_card_favorite(card_id: int, is_favorite: bool):
    return __put(f'/cards/{card_id}/favorite', {'card': {'is_favorite': is_favorite}})


def post_auth_signup(
        unique_id: str,
        nonce: str,
        captcha_session_key: Optional[str] = None
):
    headers = {
        'User-Agent': config.game_platform.user_agent,
        'Accept': '*/*',
        'Content-type': 'application/json',
        'X-Platform': config.game_platform.name,
        'X-ClientVersion': config.game_env.version_code,
    }

    data = __purge_none({
        "auth_transaction_id": nonce,
        'bundle_id': config.game_env.bundle_id,
        'device_token': 'failed' if captcha_session_key is None else captcha_session_key,
        'reason': 'unknown status code: -17' if captcha_session_key is None else None,
        'captcha_session_key': captcha_session_key,
        'user_account': {
            'ad_id': '',
            'unique_id': unique_id,
            'country': config.game_env.country,
            'currency': config.game_env.currency,
            'device': config.game_platform.device_name,
            'device_model': config.game_platform.device_model,
            'os_version': config.game_platform.os_version,
            'platform': config.game_platform.name
        }
    })

    url = config.game_env.url + '/auth/sign_up'
    res = requests.post(url, headers=headers, data=json.dumps(data))
    #__print_response(res)
    return res.json()


def post_auth_signin(
        authorization: str,
        unique_id: str,
        nonce: str,
        captcha_session_key: Optional[str] = None
):
    data = json.dumps(__purge_none({
        "auth_transaction_id": nonce,
        'bundle_id': config.game_env.bundle_id,
        'device_token': 'failed' if captcha_session_key is None else captcha_session_key,
        'reason': 'NETWORK_ERROR: null' if captcha_session_key is None else None,
        'captcha_session_key': captcha_session_key,
        'user_account': {
            'ad_id': '',
            'device': config.game_platform.device_name,
            'device_model': config.game_platform.device_model,
            "graphics_api": "vulkan1.1.0,gles3.1",
            "is_usable_astc": True,
            "os_architecture": "x86_64,x86,arm64-v8a,armeabi-v7a,armeabi",
            'os_version': config.game_platform.os_version,
            'platform': config.game_platform.name,
            'unique_id': unique_id,
            'voice': 'ja'
        }
    }))

    headers = __purge_none({
        'User-Agent': config.game_platform.user_agent,
        'Accept': '*/*',
        'Authorization': authorization,
        'Content-type': 'application/json',
        'X-ClientVersion': config.game_env.version_code,
        'X-Language': 'en',
        'X-UserCountry': config.game_env.country,
        'X-UserCurrency': config.game_env.currency,
        'X-Platform': config.game_platform.name,
    })

    url = config.game_env.url + '/auth/sign_in'
    res = requests.post(url, headers=headers, data=data)
    #__print_response(res)
    return res.json()

def request_token(code: str):
    token_url = 'https://oauth2.googleapis.com/token' 
    google_client_id = '33528429135-fg507svof8s85i1c32isr6ci5radpqqh.apps.googleusercontent.com'
    payload = {
                'audience': '33528429135-tosmtg8e15lp4l2bulmj8nc5un2ba7s3.apps.googleusercontent.com',
                'client_id': google_client_id,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'com.googleusercontent.apps.33528429135-fg507svof8s85i1c32isr6ci5radpqqh:/oauth2callback'
            }
            
    try:
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '378',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'oauth2.googleapis.com',
            'User-Agent': config.game_platform.user_agent
        }
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        token_data = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"\n--- Error during token exchange: {e} ---")
    
    return token_data["id_token"]


def post_auth_link(token: str, validate: bool=False, uid: str=''):
    data = json.dumps({
        'token':token
    })

    headers = __purge_none({
        'User-Agent': config.game_platform.user_agent,
        'Accept': '*/*',
        'Content-type': 'application/json',
        'X-ClientVersion': config.game_env.version_code,
        'X-Language': 'en',
        'X-UserCountry': config.game_env.country,
        'X-UserCurrency': config.game_env.currency,
        'X-Platform': config.game_platform.name,
    })

    url = 'https://ishin-global.aktsk.com/user/succeed/google'
    if validate:
        url = url + '/validate'
        res = requests.post(url, headers=headers, data=data)
    else:
        data = {
            'token': token,
            'user_account': {
                "device": config.game_platform.device_name,
                "device_model": config.game_platform.device_model, 
                "os_version": config.game_platform.os_version,
                "platform": config.game_platform.name, 
                "unique_id": uid 
            }
        }
        data = json.dumps(data)
        res = requests.put(url, headers=headers, data=data)

    res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return res.json()

GURL = "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=33528429135-fg507svof8s85i1c32isr6ci5radpqqh.apps.googleusercontent.com&redirect_uri=com.googleusercontent.apps.33528429135-fg507svof8s85i1c32isr6ci5radpqqh%3A%2Foauth2callback&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fgames&prompt=consent&hl=en-US"

def get_gtoken():
    return request_gtoken(google_login())

def google_login():
    code = None

    opts = Options()
    opts.add_argument('user-agent=Mozilla/5.0 (Linux; Android 12; moto g 5G (2022)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 ')
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument('--disable-blink-features=AutomationControlled')
    opts.add_argument("--disable-logging")
    opts.add_argument("--log-level=3")
    opts.add_argument(f'--app={GURL}')

    driver = webdriver.Chrome(options=opts)

    try:

        wait = ui.WebDriverWait(driver, 6000)
        wait.until(lambda d: d.requests[-1].url.startswith("https://accounts.google.com/signin/oauth/consent/approval?authuser=0") or
                             d.current_url.startswith("https://www.google.com"))

        for request in driver.requests:
            if request.url.startswith("https://accounts.google.com/signin/oauth/consent/approval?authuser=0"):
                content = request.response.body
                code = crypto.decode_gcode(content)
    except Exception as e:
        print("[Error]", e)

    driver.quit()
    return code 

def request_gtoken(code: str):
    token_url = 'https://oauth2.googleapis.com/token' 
    google_client_id = '33528429135-fg507svof8s85i1c32isr6ci5radpqqh.apps.googleusercontent.com'
    payload = {
                'audience': '33528429135-tosmtg8e15lp4l2bulmj8nc5un2ba7s3.apps.googleusercontent.com',
                'client_id': google_client_id,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': 'com.googleusercontent.apps.33528429135-fg507svof8s85i1c32isr6ci5radpqqh:/oauth2callback'
            }
            
    try:
        headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Length': '378',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'oauth2.googleapis.com',
            'User-Agent': config.game_platform.user_agent
        }
        response = requests.post(token_url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        token_data = response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"\n--- Error during token exchange: {e} ---")
    
    return token_data["id_token"]


def post_link(token: str):
    data = json.dumps({
        'token':token
    })
    headers = __generate_headers('POST', '/user/link/google')
    url = 'https://ishin-global.aktsk.com/user/link/google'
    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return res.json()


def post_auth_link(token: str, validate: bool=False, uid: str=''):
    data = json.dumps({
        'token':token
    })

    headers = __purge_none({
        'User-Agent': config.game_platform.user_agent,
        'Accept': '*/*',
        'Content-type': 'application/json',
        'X-ClientVersion': config.game_env.version_code,
        'X-Language': 'en',
        'X-UserCountry': config.game_env.country,
        'X-UserCurrency': config.game_env.currency,
        'X-Platform': config.game_platform.name,
    })

    url = 'https://ishin-global.aktsk.com/user/succeed/google'
    if validate:
        url = url + '/validate'
        res = requests.post(url, headers=headers, data=data)
    else:
        data = {
            'token': token,
            'user_account': {
                "device": config.game_platform.device_name,
                "device_model": config.game_platform.device_model, 
                "os_version": config.game_platform.os_version,
                "platform": config.game_platform.name, 
                "unique_id": uid 
            }
        }
        data = json.dumps(data)
        res = requests.put(url, headers=headers, data=data)

    res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    return res.json()

def post_login_bonuses_accept():
    return __post('/login_bonuses/accept')


def post_gifts_accept(gift_ids: list):
    return __post('/gifts/accept', {'gift_ids': gift_ids})


def post_missions_accept(mission_ids: list):
    return __post('/missions/accept', {'mission_ids': mission_ids})


def post_teams(
        selected_team_num: int,
        user_card_teams: list
): return __post('/teams', {
    'selected_team_num': selected_team_num,
    'user_card_teams': user_card_teams
})


def post_rmbattles_start(
        clash_id: str,
        stage_id: str,
        is_beginning: bool,
        leader: Any,
        members: list[Any],
        sub_leader: Any
): return __post('/rmbattles/' + clash_id + '/stages/' + stage_id + '/start', {
    'is_beginning': is_beginning,
    'user_card_ids': {
        'leader': leader,
        'members': members,
        'sub_leader': sub_leader
    }
})


def post_rmbattles_dropout(clash_id: str):
    return __post('/rmbattles/' + clash_id + '/stages/dropout', {'reason': 'dropout'})


def post_rmbattles_finish(
        clash_id: str,
        damage: int,
        finished_at_ms: int,
        finished_reason: str,
        is_cleared: bool,
        remaining_hp: int,
        round: int,
        started_at_ms: int,
        token: str
): __post('/rmbattles/' + clash_id + '/stages/finish', {
    'damage': damage,
    'finished_at_ms': finished_at_ms,
    'finished_reason': finished_reason,
    'is_cleared': is_cleared,
    'remaining_hp': remaining_hp,
    'round': round,
    'started_at_ms': started_at_ms,
    'token': token
})


def post_quests_sugoroku_start(stage_id: int, sign: str):
    return __post('/quests/' + str(stage_id) + '/sugoroku_maps/start', {
        'sign': sign
    })


def post_quests_sugoroku_finish(stage_id: int, sign: str):
    return __post('/quests/' + str(stage_id) + '/sugoroku_maps/finish', {
        'sign': sign
    })


def post_zbattles_start(stage_id: str, sign: str):
    return __post('/z_battles/' + stage_id + '/start', {
        'sign': sign
    })


def post_zbattles_finish(
        stage_id: str,
        elapsed_time: int,
        is_cleared: bool,
        level: int,
        s: str,
        t: str,
        token: str,
        used_items: list,
        z_battle_finished_at_ms: int,
        z_battle_started_at_ms: int,
        reason: Optional[str]
):
    return __post('/z_battles/' + stage_id + '/finish', {
        'elapsed_time': elapsed_time,
        'is_cleared': is_cleared,
        'level': level,
        's': s,
        't': t,
        'token': token,
        'reason': reason,
        'used_items': used_items,
        'z_battle_started_at_ms': z_battle_started_at_ms,
        'z_battle_finished_at_ms': z_battle_finished_at_ms
    })


def post_dragonball_sets_wishes(set: str, dragonball_wish_ids: list[int]):
    return __post('/dragonball_sets/' + set + '/wishes', {'dragonball_wish_ids': dragonball_wish_ids})


def post_user_capacity_card():
    return __post('/user/capacity/card')

def post_cards_sell(card_ids: list):
    endpoint = '/cards/sell'
    headers = __generate_headers('POST', endpoint)
    payload = {'card_ids': card_ids}
    url = config.game_env.url + endpoint
    #print("[DEBUG] URL:", url)
    #print("[DEBUG] Headers:", headers)
    #print("[DEBUG] Payload:", payload)
    res = requests.post(url, headers=headers, data=json.dumps(payload))
    #print("[DEBUG] Response text:", res.text)
    __print_response(res)
    return res.json() if res.status_code != 204 else None



def post_awakening_item_exchange(awakening_item_id: int, quantity: int):
    return __post('/awakening_items/exchange', {
        'awakening_item_id': awakening_item_id,
        'quantity': quantity
    })


def post_gashas_draw(summon_id: str, type: str):
    return __post('/gashas/' + summon_id + '/courses/' + type + '/draw')


def post_tutorial_gasha(progress: int):
    return __post('/tutorial/gasha', {'progress': progress})


def post_missions_put_forward():
    return __post('/missions/put_forward')
