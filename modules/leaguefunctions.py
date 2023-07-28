import os
import requests
import time
import json
import asyncio
import aiohttp


from base64 import b64encode
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from aiohttp_retry import ExponentialRetry, RetryClient


retry_options = ExponentialRetry(attempts=5, factor=0.5, statuses=[404, 500, 502, 503, 504])
client_session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False))
retry_client = RetryClient(client_session=client_session, retry_options=retry_options)


def get_lock_file():
    path_file = "C:/Riot Games/League of Legends/lockfile"

    if os.path.exists(path_file):
        with open(path_file, encoding="UTF-8") as lock_file:
            return lock_file.read().split(":")
        
def encrypt_headers():
    while get_lock_file() is None:
        time.sleep(1)
    password = get_lock_file()[3]
    base64 = b64encode(bytes(f"riot:{password}", "UTF-8"))
    return {"Authorization": f"Basic {base64.decode('ASCII')}"}

def get_url(end_point: str) -> str:
    while get_lock_file() is None:
        time.sleep(1)
    method = get_lock_file()[4]
    port = get_lock_file()[2]
    return f"{method}://127.0.0.1:{port}/{end_point}"

async def get_summoner_id(client : RetryClient) -> str:
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = await client.get(url, headers=headers)
    json = await response.json()
    await client.close()
    return json["summonerId"]

async def get_summoner_puuid(client : RetryClient) -> str:
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = await client.get(url, headers=headers)
    json = await response.json()
    await client.close()
    return json["puuid"]

async def get_summoner_data(client : RetryClient) -> str:
    summoner_ep = "lol-summoner/v1/current-summoner"
    headers = encrypt_headers()
    url = get_url(summoner_ep)
    response = await client.get(url, headers=headers)
    json = await response.json()
    summoner_name = json["displayName"]
    summoner_level = json["summonerLevel"]
    await client.close()
    return summoner_name, summoner_level

async def get_ranked_info(client : RetryClient) -> str:
    summoner_puuid = get_summoner_puuid()
    ranked_ep = f"lol-ranked/v1/ranked-stats/{summoner_puuid}"
    headers = encrypt_headers()
    url = get_url(ranked_ep)
    response = await client.get(url, headers=headers)
    json = await response.json()
    ranked_stats = json["queueMap"]["RANKED_SOLO_5x5"]
    if ranked_stats["tier"] == "":
        summoner_rank = "UNRANKED"
        summoner_lp = "0"
    else:
        summoner_rank = ranked_stats["tier"] + " " + ranked_stats["division"]
        summoner_lp = ranked_stats["leaguePoints"]
    summoner_wins = ranked_stats["wins"]
    summoner_losses = ranked_stats["losses"]
    if summoner_wins == 0 or summoner_losses == 0:
        summoner_winrate = "0%"
    else:
        summoner_winrate = str(round((int(ranked_stats["wins"])/int(ranked_stats["wins"] + int(ranked_stats["losses"])))*100, 2)) + "%"
    await client.close()
    return summoner_rank, summoner_lp, summoner_wins, summoner_losses, summoner_winrate

async def get_currencies(client : RetryClient) -> str:
    currency_ep = "lol-store/v1/wallet"
    headers = encrypt_headers()
    url = get_url(currency_ep)
    response = await client.get(url, headers=headers)
    json = await response.json()
    be_amount = json["ip"]
    rp_amount = json["rp"]
    if be_amount >= 1000:
        be_amount = f"{str(round(be_amount / 1000, 2))}K"
    if rp_amount >= 1000:
        rp_amount = f"{str(round(rp_amount / 1000, 2))}K"
    return be_amount, rp_amount

def is_signed_in():
    login_ep = "lol-login/v1/session"
    headers = encrypt_headers()
    url = get_url(login_ep)
    response = requests.get(url, headers=headers, verify=False)
    return response.status_code