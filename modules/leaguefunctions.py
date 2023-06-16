import os
import requests
import time
import json

from base64 import b64encode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


session = requests.Session()


def get_lock_file():
    path_file = "C:/Riot Games/League of Legends/lockfile"

    if os.path.exists(path_file):
        with open(path_file, encoding="UTF-8") as lock_file:
                lock_file_data = lock_file.read().split(":")
                return lock_file_data
        
def encrypt_headers():
    while get_lock_file() == None:
        time.sleep(1)
    password = get_lock_file()[3]
    base64 = b64encode(bytes(f"riot:{password}", "UTF-8"))
    return {"Authorization": f"Basic {base64.decode('ASCII')}"}

def get_url(end_point: str) -> str:
    while get_lock_file() == None:
        time.sleep(1)
    method = get_lock_file()[4]
    port = get_lock_file()[2]
    return f"{method}://127.0.0.1:{port}/{end_point}"

def get_summoner_id():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers).json()
    return response["summonerId"]

def get_summoner_puuid():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers).json()
    return response["puuid"]

def get_summoner_data():
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers).json()
    summoner_name = response["displayName"]
    summoner_level = response["summonerLevel"]
    return summoner_name, summoner_level

def get_ranked_info():
    summoner_puuid = get_summoner_puuid()
    ranked_ep = f"lol-ranked/v1/ranked-stats/{summoner_puuid}"
    headers = encrypt_headers()
    url = get_url(ranked_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers).json()
    ranked_stats = response["queueMap"]["RANKED_SOLO_5x5"]
    if ranked_stats["tier"] == "":
        summoner_rank = "UNRANKED"
        summoner_lp = "0"
    else:
        summoner_rank = ranked_stats["tier"] + " " + ranked_stats["division"]
        summoner_lp = ranked_stats["leaguePoints"]
    summoner_wins = ranked_stats["wins"]
    summoner_losses = ranked_stats["losses"]
    if summoner_wins == 0 or summoner_losses == 0:
        summoner_winrate = "UNRANKED"
    else:
        summoner_winrate = str(round((int(ranked_stats["wins"])/int(ranked_stats["wins"] + int(ranked_stats["losses"])))*100, 2)) + "%"
    return summoner_rank, summoner_lp, summoner_wins, summoner_losses, summoner_winrate

def get_currencies():
    currency_ep = "lol-store/v1/wallet"
    headers = encrypt_headers()
    url = get_url(currency_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers).json()
    be_amount = response["ip"]
    rp_amount = response["rp"]
    if be_amount >= 1000:
        be_amount = str(round(be_amount/1000, 2)) + "K"
    if rp_amount >= 1000:
        rp_amount = str(round(rp_amount/1000, 2)) + "K"
    return be_amount, rp_amount

def is_signed_in():
    login_ep = "lol-login/v1/session"
    headers = encrypt_headers()
    url = get_url(login_ep)
    session.mount(url, HTTPAdapter(max_retries=Retry(connect=30, backoff_factor=0.5, status_forcelist=[404, 500, 502, 503, 504])))
    response = session.get(url, verify=False, headers=headers)
    return response.status_code