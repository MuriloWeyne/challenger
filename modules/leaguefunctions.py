import os
import requests

from base64 import b64encode


def get_lock_file():
    path_file = "C:/Riot Games/League of Legends/lockfile"

    if os.path.exists(path_file):
        with open(path_file, encoding="UTF-8") as lock_file:
                lock_file_data = lock_file.read().split(":")
                return lock_file_data
    
def encrypt_headers():
    password = get_lock_file()[3]
    base64 = b64encode(bytes(f"riot:{password}", "UTF-8"))
    return {"Authorization": f"Basic {base64.decode('ASCII')}"}

def get_url(end_point: str) -> str:
    method = get_lock_file()[4]
    port = get_lock_file()[2]
    return f"{method}://127.0.0.1:{port}/{end_point}"

def get_summoner_id():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = requests.get(url, verify=False, headers=headers).json()
    return response["summonerId"]

def get_summoner_puuid():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = requests.get(url, verify=False, headers=headers).json()
    return response["puuid"]

def get_summoner_data():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = requests.get(url, verify=False, headers=headers).json()
    summoner_name = response["displayName"]
    summoner_level = response["summonerLevel"]
    return summoner_name, summoner_level

def get_ranked_info():
    summoner_puuid = get_summoner_puuid()
    ranked_ep = f"lol-ranked/v1/ranked-stats/{summoner_puuid}"
    headers = encrypt_headers()
    url = get_url(ranked_ep)
    response = requests.get(url, verify=False, headers=headers).json()       
    ranked_stats = response["queueMap"]["RANKED_SOLO_5x5"]
    summoner_rank = ranked_stats["tier"] + " " + ranked_stats["division"]
    summoner_lp = ranked_stats["leaguePoints"]
    summoner_wins = ranked_stats["wins"]
    summoner_losses = ranked_stats["losses"]
    summoner_winrate = str(round((int(ranked_stats["wins"])/int(ranked_stats["wins"] + int(ranked_stats["losses"])))*100, 2)) + "%"
    return summoner_rank, summoner_lp, summoner_wins, summoner_losses, summoner_winrate

def get_currencies():
    currencies_ep = "lol-store/v1/wallet"
    headers = encrypt_headers()
    url = get_url(currencies_ep)
    response = requests.get(url, verify=False, headers=headers).json()
    be_amount = response["ip"]
    if be_amount >= 1000:
        be_amount = str(round(be_amount/1000, 2)) + "K"
    return response["rp"], be_amount