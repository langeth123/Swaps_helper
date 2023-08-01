from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from loguru import logger
from Modules.Decrypt import *
import json
from os import getcwd
from Modules.Encryptor import *
import asyncio
from time import sleep
import time
import random
import web3
from eth_account import Account as acc
from web3.eth import AsyncEth

SETTINGS_PATH = getcwd() + '\\data\\'

with open(f"{SETTINGS_PATH}settings.json", "r", encoding='utf-8') as file:
    SETTINGS = json.load(file)

with open(f"{SETTINGS_PATH}abi\\erc20.json", "r", encoding='utf-8') as file:
    ERC20_ABI = json.load(file)

with open(f"{SETTINGS_PATH}to_run_addresses.txt", "r", encoding='utf-8') as f:
    SECRETS = [row.strip() for row in f]

with open(f"{SETTINGS_PATH}proxies.txt", "r", encoding='utf-8') as f:
    PROXIES = [row.strip() for row in f]

if SETTINGS["TaskNumber"] == 11:
    logger.info("Here is encryptor settings. 1 - encrypt to_encrypted_secrets.txt by Flash or any disk")
    logger.info("Here is encryptor settings. 2 - encrypt to_encrypted_secrets.txt by Password")
    while True:
        answer = input("Choose task number: ").replace(" ", "")
        if answer.isdigit():
            logger.info(f"OK, you choose task number: {answer}")
            if answer in ["1", "2"]:
                break
        else:
            logger.error("Answer is not digit")
    
    if answer == '1':
        encrypt('flash', SETTINGS_PATH)
    if answer == '2':
        encrypt('password', SETTINGS_PATH)

def decrypt():
    global runner_secrets
    secrets = decrypt_files(SETTINGS.get("DecryptType"), SETTINGS.get("LoaderDisk"), SETTINGS_PATH)
    addresses = [i.replace("\n", "") for i in SECRETS]
    runner_secrets = [secrets.get(i.lower()) for i in addresses if secrets.get(i.lower()) is not None]

    if len(runner_secrets) == 0:
        logger.error(f'Bot cant find any secret keys to start work! Check again your settings and to_run_addresses.txt file')
        input("Press any key to end work")
        exit()
    else:
        logger.success(f"Bot found: {len(runner_secrets)} accounts to run")

decrypt()
CONNECTED_RPCS = {}
PROXIES_RPCS = {}

CONNECTED_OUR_RPCS = {}

async def connect_to_all_rpcs():
    for net_name in SETTINGS["RPC"].keys():
        temp = []

        for i in SETTINGS["RPC"][net_name]:
            web3 = Web3(HTTPProvider(i))
            temp.append(web3)
        
        CONNECTED_RPCS.update({net_name: temp})
    logger.success("Soft connected to all custom rpc's")

asyncio.run(connect_to_all_rpcs())

ASYNC_RPC = {}
ASYNC_OUR_RPC = {}

async def async_connect_to_all_rpcs():
    for net_name in SETTINGS["RPC"].keys():
        temp = []

        for i in SETTINGS["RPC"][net_name]:
            web3 = Web3(
                AsyncHTTPProvider(i),
                modules={"eth": (AsyncEth,)},
                middlewares=[],
            )
            temp.append(web3)
        
        ASYNC_RPC.update({net_name: temp})
    logger.success("Soft connected to all async rpc's")
            
asyncio.run(async_connect_to_all_rpcs())

def sleeping(disc: str, bridge=False) -> None:
    if bridge:
        from_sleep = SETTINGS["BridgeSleep"][0]
        to_sleep = SETTINGS["BridgeSleep"][1]
    else:
        from_sleep = SETTINGS["TaskSleep"][0]
        to_sleep = SETTINGS["TaskSleep"][1]
    x = random.randint(from_sleep, to_sleep)
    logger.info(f'Disc: {disc} | sleeping: {x} s')
    time.sleep(x)




NATIVE = {
    "ethereum"  : "$ETH",
    "bsc"       : "$BNB",
    "fantom"    : "$FTM",
    "polygon"   : "$MATIC",
    "arbitrum"  : "$ETH",
    "avalanche" : "$AVAX",
    "optimism"  : "$ETH"
}


def get_random_number(settings_name: str) -> int:
    return random.randint(SETTINGS[settings_name][0], SETTINGS[settings_name][1])



STARGATE = {
    "bsc"       : ["0x55d398326f99059fF775485246999027B3197955"],
    "avalanche" : ["0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7", "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"],
    "arbitrum"  : ["0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"],
    "polygon"   : ["0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"],
    "fantom"    : ["0x28a92dde19D9989F39A49905d7C9C2FAc7799bDf"]
}